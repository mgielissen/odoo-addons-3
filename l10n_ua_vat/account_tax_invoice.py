# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class TaxInvoice(models.Model):
	_name = 'account.taxinvoice'
	_description = 'Tax Invoice'
    
	h01 = fields.Integer(string = 'Skladaetsya investorom', default = 0)
	horig1 = fields.Integer(string = 'Ne vydaetsya pokuptsyu', default = 0)
	htypr = fields.Integer(string = 'Typ prychyny', default = 0)

	date_vyp = fields.Date(string='Data dokumentu', index=True,				# TODO readonly=True, states={'draft': [('readonly', False)]},
        help="Data pershoi podii z PDV", copy=True, required=True)

	date_reg = fields.Date(string='Data reestracii', index=True,				# TODO readonly=True, states={'draft': [('readonly', False)]},
        help="Data reestracii dokumentu v ERPN", copy=False)

  	number = fields.Char(string = 'Nomer PN')
	number1 = fields.Integer(string = 'Oznaka specialnoi PN')
	number2 = fields.Integer(string = 'Kod Filii')

	category = fields.Selection([
        ('out_tax_invoice','Vydani PN'),
        ('in_tax_invoice','Otrymani PNН'),
        ], string='Category', readonly=True, index=True, 
        change_default=True, default=lambda self: self._context.get('category', 'out_tax_invoice'), 
        track_visibility='always')

	doc_type = fields.Selection([
        ('pn','Podatkova nakladna'),
        ('rk','Rozrakhunok koryguvannya do PN'),
        ('vmd','Mytna deklaratsiya'),
        ('tk','Transportnyj kvytok'),
        ('bo','Buhgalterska dovidka'),
        ], string='Typ dokumentu', index=True, 
        change_default=True, default='pn', 
        track_visibility='always')

	# Modified record name on form view
	@api.multi
	def name_get(self):
		TYPES = {
			'pn': 'Podatkova nakladna',
			'rk': 'Rozrakhunok koryguvannya do PN',
			'vmd': 'Mytna deklaratsiyaя',
			'tk': 'Transportnyj kvytok',
			'bo': 'Buhgalterska dovidka',
		}
		result = []
		for inv in self:
			date = fields.Date.from_string(inv.date_vyp)
			datef = date.strftime('%d.%m.%Y')
			result.append((inv.id, "%s # %s vid %s" % (TYPES[inv.doc_type], inv.number, datef)))
		return result