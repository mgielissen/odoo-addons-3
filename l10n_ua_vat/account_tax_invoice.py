# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class TaxInvoice(models.Model):
	_name = 'account.taxinvoice'
	_description = 'Tax Invoice'
    
	date_vyp = fields.Date(string='Дата документу', index=True,				# TODO readonly=True, states={'draft': [('readonly', False)]},
        help="Дата першої події з ПДВ", copy=True, required=True)

	date_reg = fields.Date(string='Дата реєстрації', index=True,				# TODO readonly=True, states={'draft': [('readonly', False)]},
        help="Дата реєстрації документу в ЄРПН", copy=False)

  	number = fields.Char(string = ' Номер ПН')
	number1 = fields.Integer(string = 'Ознака спеціальної ПН')
	number2 = fields.Integer(string = 'Код філії')

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

	# Modificated record name on form view
	@api.multi
	def name_get(self):
		TYPES = {
			'pn': _('Податкова накладна'),
			'rk': _('Розрахунок коригування до ПН'),
			'vmd': _('Митна декларація'),
			'tk': _('Транспортний квиток'),
			'bo': _('Бухгалтерська довідка'),
		}
		result = []
		for inv in self:
			date = fields.Date.from_string(inv.date_reg)
			datef = date.strftime('%d.%m.%Y')
			result.append((inv.id, _("%s № %s від %s") % (TYPES[inv.doc_type], inv.number, datef)))
		return result