# -*- coding: utf-8 -*-

from openerp import models, fields, api

class TaxInvoice(models.Model):
	_name = 'uatax.invoice'
	_description = 'Tax Invoice'
    
	name = fields.Char(string="Title", required=True)
 