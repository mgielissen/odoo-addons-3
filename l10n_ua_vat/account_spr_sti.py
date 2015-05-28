# -*- coding: utf-8 -*-

from openerp import models, fields, api

class SprSti(models.Model):
	_name = 'account.sprsti'
	_description = 'Dovidnyk STI'

	c_sti = fields.Integer(string="Код ДПІ", required=True)
	c_raj = fields.Integer(string="Код району", required=True)
	t_sti = fields.Integer(string="Тип ДПІ", required=True)
	name = fields.Char(string="Найменування", required=True)
	name_raj = fields.Char(string="Район", required=True)
# Add sti menu to account->contig->misc
# Add field to res.conpany to select sti 
