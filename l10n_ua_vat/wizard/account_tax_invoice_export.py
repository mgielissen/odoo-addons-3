# -*- coding: utf-8 -*-

import base64
import cStringIO
import zipfile
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning, UserError


class TaxInvoiceExport(models.TransientModel):
    _name = 'account.taxinvoice.export'
    _description = "Export the selected tax invoices"

    fname = fields.Char(string=u"File Name",
                        readonly=True,
                        default='default.txt')
    fdata = fields.Binary(string=u"File data",
                          readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('download', 'Download')],
                             string="State",
                             default='draft')

    @api.multi
    def taxinvoice_export(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        active_ids = context.get('active_ids', []) or []
        mf = cStringIO.StringIO()
        with zipfile.ZipFile(mf, mode='w') as zf:
            for record in self.env['account.taxinvoice'].browse(active_ids):
                buf, filename = record._export_xml_data()
                zf.writestr(filename, buf)
        #     if record.state not in ('ready'):
        #         raise UserError(_(u"Обрані ПН не готові до вивантаження"))
        #     record.signal_workflow('invoice_open')
        data = base64.encodestring(mf.getvalue())
        mf.close()
        name = "your_PNs.zip"
        self.write({'state': 'download', 'fdata': data, 'fname': name})
        return {
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'res_model': 'account.taxinvoice.export',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }
