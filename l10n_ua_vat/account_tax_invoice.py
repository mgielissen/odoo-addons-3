# -*- coding: utf-8 -*-

from openerp import models, fields, api

class SprSti(models.Model):
	_name = 'account.sprsti'
	_description = 'Dovidnyk STI'

	c_sti = fields.Integer(string="Код ДПІ", required=True)
	c_raj = fields.Integer(string="Код району", required=True)
	t_sti = fields.Integer(string="Тип ДПІ", required=True)
	name_sti = fields.Char(string="Найменування", required=True)
	name_raj = fields.Char(string="Район", required=True)
# Add sti menu to account->contig->misc
# Add field to res.conpany to select sti


class TaxInvoice(models.Model):
	_name = 'account.taxinvoice'
	_description = 'Tax Invoice'
    
	date_vyp = fields.Date(string='Дата документу', index=True,				# TODO readonly=True, states={'draft': [('readonly', False)]},
        help="Дата першої події з ПДВ", copy=True, required=True)

	date_reg = fields.Date(string='Дата реєстрації', index=True,				# TODO readonly=True, states={'draft': [('readonly', False)]},
        help="Дата реєстрації документу в ЄРПН", copy=False)

#	name = fields.Char(string="Title", required=True)

	category = fields.Selection([
            ('out_tax_invoice','Видані ПН'),
            ('in_tax_invoice','Отримані ПН'),
        	], string='Category', readonly=True, index=True, 
        	change_default=True, default='out_tax_invoice', 
        	track_visibility='always')

	doc_type = fields.Selection([
            ('pn','Податкова накладна'),
            ('rk','Розрахунок коригування до ПН'),
            ('vmd','Митна декларація'),
            ('tk','Транспортний квиток'),
            ('bo','Бухгалтерська довідка'),
        	], string='Тип документу', index=True, 
        	change_default=True, default='pn', 
        	track_visibility='always')
 