# -*- coding: utf-8 -*-

import base64
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning, UserError


class TaxInvoiceExportSingle(models.TransientModel):
    _name = 'account.taxinvoice.export_single'
    _description = "Export single tax invoice"

    @api.model
    def _get_pn_number(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            tinv = self.env['account.taxinvoice'].browse(active_id)
            return str(tinv.number)
        return 'nema'

    # @api.model
    # def _get_name(self):
    #     context = dict(self.env.context or {})
    #     active_id = context.get('active_id', False)
    #     if active_id:
    #         tinv = self.env['account.taxinvoice'].browse(active_id)
    #         return "%s.xml" % tinv.number
    #     return 'PN.txt'

    fname = fields.Char(string=u"File Name",
                        readonly=True,
                        default='PN.xml')
    fdata = fields.Binary(string=u"File data",
                          readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('download', 'Download')],
                             string="State",
                             default='draft')
    pn_numb = fields.Char(string=u"Номер податкової накладної",
                          readonly=False,
                          default=_get_pn_number)

    @api.multi
    def single_taxinvoice_export(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        active_id = context.get('active_id', []) or []
        buf = ''
        tinv = self.env['account.taxinvoice'].browse(active_id)
        #     if record.state not in ('ready'):
        #         raise UserError(_(u"Обрані ПН не готові до вивантаження"))
        #     record.signal_workflow('invoice_open')
        buf, name = tinv._export_xml_data()
        data = base64.encodestring(buf)
        self.write({'state': 'download', 'fdata': data, 'fname': name})
        return {
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'res_model': 'account.taxinvoice.export_single',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }
