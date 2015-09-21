# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SprSti(models.Model):
    _name = 'account.sprsti'
    _description = u"Довідник ДПІ"

    c_sti = fields.Integer(string=u"Код ДПІ", required=True)
    c_raj = fields.Integer(string=u"Код району", required=True)
    t_sti = fields.Integer(string=u"Тип ДПІ", required=True)
    name = fields.Char(string=u"Назва", required=True)
    name_raj = fields.Char(string=u"Район", required=True)
