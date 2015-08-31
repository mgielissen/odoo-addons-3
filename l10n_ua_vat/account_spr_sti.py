# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SprSti(models.Model):
    _name = 'account.sprsti'
    _description = 'Dovidnyk STI'

    c_sti = fields.Integer(string="Kod DPI", required=True)
    c_raj = fields.Integer(string="Kod rayonu", required=True)
    t_sti = fields.Integer(string="Typ DPI", required=True)
    name = fields.Char(string="Naimenuvannya", required=True)
    name_raj = fields.Char(string="Rayon", required=True)
