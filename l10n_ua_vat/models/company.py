# -*- coding: utf-8 -*-

from openerp import fields, models


class CompanySti(models.Model):
    _inherit = 'res.company'

    # Add a new column to the res.company model
    comp_sti = fields.Many2one('account.sprsti',
                               string=u"Податковий орган", ondelete='set null',
                               help=u"Виберіть ДПІ в якій взято на облік "
                               u"ваше підприємство",
                               index=True)
