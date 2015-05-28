# -*- coding: utf-8 -*-

from openerp import fields, models

class CompanySti(models.Model):
    _inherit = 'res.company'

    # Add a new column to the res.company model
    comp_sti = fields.Many2one('account.sprsti',
        string="Podatkovyj organ", ondelete='set null', 
        help='Vyberit DPI v yakij vzyato na oblik pidpryemstvo', index=True)