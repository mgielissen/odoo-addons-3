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
            raise UserError(_(u"ІПН %s покупця не співпадає "
                              u"з ІПН вашої організації!" % hkbuy.text))
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
        ctx['state'] = 'draft'
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
        tax_invoice = acc_ti.with_context(ctx).create({
            'state': 'draft',
            'h01': True if declarbody.find('H01').text == '1' else False,
            'horig1': True if declarbody.find('HORIG1').text == '1' else False,
            'htypr': declarbody.find('HTYPR').text or '00',
            'date_vyp': fields.Date.to_string(date),
            'number': declarbody.find('HNUM').text or '0',
            'number1': declarbody.find('HNUM1').text or None,
            'number2': declarbody.find('HNUM2').text or None,
            'category': 'in_tax_invoice',
            'doc_type': 'pn',
            'partner_id': partner_id.id,
            'ipn_partner': hksel.text,
            'adr_partner': declarbody.find('HLOCSEL').text or ' ',
            'tel_partner': declarbody.find('HTELSEL').text or None,
            'contract_date': cont_date,
            'contract_numb': declarbody.find('H01G3S').text or None,
            'prych_zv': declarbody.find('R003G10S').text or None,
            'currency_id': currency.id,
            'journal_id': journal.id,
            'company_id': company_id.id,
            'account_id': account.id,
            'amount_tara': float(declarbody.find('R02G11').text or 0)})
        # now add tax lines to tax invoice
        ti_taxline = self.env['account.taxinvoice.tax']
        domain = [('type_tax_use', '=', 'purchase'),
                  ('company_id', '=', company_id.id),
                  ('name', 'like', u'ПДВ')]
        for tax in self.env['account.tax'].search(domain):
            if tax.name.find(u"ПДВ 20%") >= 0:
                if float(declarbody.find('R01G7').text or 0) > 0.0:
                    base = float(declarbody.find('R01G7').text)
                    amount = float(declarbody.find('R03G7').text)
                    ti_taxline.with_context(ctx).create({
                        'taxinvoice_id': tax_invoice.id,
                        'name': tax.name,
                        'tax_id': tax.id,
                        'base': base,
                        'amount': amount,
                        'manual': False,
                        'sequence': tax.sequence,
                        'account_analytic_id': tax.analytic or False,
                        'account_id': tax.account_id.id or False})
            if tax.name.find(u"ПДВ 7%") >= 0:
                if float(declarbody.find('R01G109').text or 0) > 0.0:
                    base = float(declarbody.find('R01G109').text)
                    amount = float(declarbody.find('R03G109').text)
                    ti_taxline.with_context(ctx).create({
                        'taxinvoice_id': tax_invoice.id,
                        'name': tax.name,
                        'tax_id': tax.id,
                        'base': base,
                        'amount': amount,
                        'manual': False,
                        'sequence': tax.sequence,
                        'account_analytic_id': tax.analytic or False,
                        'account_id': tax.account_id.id or False})
            if tax.name.find(u"ПДВ 0%") >= 0:
                base = amount = 0.0
                if float(declarbody.find('R01G9').text or 0) > 0.0:
                    base += float(declarbody.find('R01G9').text)
                if float(declarbody.find('R01G8').text or 0) > 0.0:
                    base += float(declarbody.find('R01G8').text)
                if base > 0.0:
                    ti_taxline.with_context(ctx).create({
                        'taxinvoice_id': tax_invoice.id,
                        'name': tax.name,
                        'tax_id': tax.id,
                        'base': base,
                        'amount': amount,
                        'manual': False,
                        'sequence': tax.sequence,
                        'account_analytic_id': tax.analytic or False,
                        'account_id': tax.account_id.id or False})
            if tax.name.find(u"від ПДВ") >= 0:
                if float(declarbody.find('R01G10').text or 0) > 0.0:
                    base = float(declarbody.find('R01G10').text)
                    amount = 0.0
                    ti_taxline.with_context(ctx).create({
                        'taxinvoice_id': tax_invoice.id,
                        'name': tax.name,
                        'tax_id': tax.id,
                        'base': base,
                        'amount': amount,
                        'manual': False,
                        'sequence': tax.sequence,
                        'account_analytic_id': tax.analytic or False,
                        'account_id': tax.account_id.id or False})
        # we can't write to computed fields, so recompute them
        tax_invoice._compute_amount()
        # workflow can only be started from draft, so we move it to sent
        tax_invoice.signal_workflow('taxinvoice_ready')
        tax_invoice.signal_workflow('taxinvoice_sent')
        return True
