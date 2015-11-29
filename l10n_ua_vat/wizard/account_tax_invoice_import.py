# -*- coding: utf-8 -*-

import base64
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning, UserError
import xml.etree.ElementTree as ET
import datetime


class TaxInvoiceImport(models.TransientModel):
    _name = 'account.taxinvoice.import'
    _description = "Import single tax invoice"

    fname = fields.Char(string=u"File Name",
                        readonly=False)
    fdata = fields.Binary(string=u"File data",
                          readonly=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done')],
                             string="State",
                             default='draft')

    @api.multi
    def taxinvoice_import(self):
        self.ensure_one()
        company_id = self._context.get('company_id',
                                       self.env.user.company_id)

        try:
            root = ET.fromstring(base64.b64decode(self.fdata))
        except ET.ParseError:
            raise UserError(_(u"Невірний формат xml файлу!"))

        declarbody = root.find('DECLARBODY')
        if declarbody is None:
            raise UserError(_(u"Невірний формат файлу"))
            return True
        # check if we are buyers
        hkbuy = declarbody.find('HKBUY')
        if hkbuy is None:
            raise UserError(_(u"Невірний формат файлу"))
            return True
        if hkbuy.text.find(company_id.vat) < 0:
            raise UserError(_(u"ІПН покупця не співпадає "
                              u"з ІПН вашої організації!"))
        # check if partner is already in database
        hksel = declarbody.find('HKSEL')
        if hksel is None:
            raise UserError(_(u"Невірний формат файлу"))
            return True
        domain = [('vat', '=', hksel.text),
                  ('supplier', '=', True),
                  ('is_company', '=', True)]
        partner_id = self.env['res.partner'].search(domain, limit=1)
        if len(partner_id) == 0:
            raise UserError(_(u"Немає продавця з таким ІПН %s" % hksel.text))
            return True
        # Ok let's write taxinvoice
        ctx = dict(self._context)
        ctx['company_id'] = company_id.id
        ctx['category'] = 'in_tax_invoice'
        date = datetime.datetime.strptime(declarbody.find('HFILL').text,
                                          '%d%m%Y').date()
        cd = declarbody.find('H01G2D')
        if cd is None or cd.text is None:
            cont_date = None
        else:
            cont_date = \
             fields.Date.to_string(datetime.datetime.strptime(cd.text,
                                                              '%d%m%Y').date())
        acc_ti = self.env['account.taxinvoice']
        account = acc_ti.with_context(ctx)._default_account()
        journal = acc_ti.with_context(ctx)._default_journal()
        currency = acc_ti.with_context(ctx)._default_currency()
        acc_ti.with_context(ctx).create({
            'state': 'sent',
            'h01': True if declarbody.find('H01').text == '1' else False,
            'horig1': True if declarbody.find('HORIG1').text == '1' else False,
            'htypr': declarbody.find('HTYPR').text or '00',
            'date_vyp': fields.Date.to_string(date),
            'number': declarbody.find('HNUM').text or '0',
            'number1': declarbody.find('HNUM1').text or '',
            'number2': declarbody.find('HNUM2').text or '',
            'category': 'in_tax_invoice',
            'doc_type': 'pn',
            'partner_id': partner_id.id,
            'ipn_partner': hksel.text,
            'adr_partner': declarbody.find('HLOCSEL').text or ' ',
            'tel_partner': declarbody.find('HTELSEL').text or '0',
            'contract_date': cont_date,
            'contract_numb': declarbody.find('H01G3S').text or '',
            'prych_zv': declarbody.find('R003G10S').text or '',
            'currency_id': currency.id,
            'journal_id': journal.id,
            'company_id': company_id.id,
            'account_id': account.id,
            'amount_untaxed': float(declarbody.find('R01G11').text) or 0.00,
            'amount_tara': float(declarbody.find('R02G11').text) or 0.00,
            'amount_tax': float(declarbody.find('R03G11').text) or 0.00,
            'amount_total': float(declarbody.find('R04G11').text) or 0.00,
        })
