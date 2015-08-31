# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class TaxInvoiceExport(models.TransientModel):
    _name = 'account.taxinvoice.export'
    _description = "Confirm the selected invoices"

    # see account/wizard/account_invoice_state.py (old api there)
    @api.one
    def taxinvoice_export(self):
        return {'type': 'ir.actions.act_window_close'}
