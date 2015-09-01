# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class ProductTemplUktZed(models.Model):
    _inherit = 'product.template'

    ukt_zed = fields.Char(related='product_variant_ids.ukt_zed',
                          string='Kod UKT ZED',
                          help="Kod zgidno UKT ZED",
                          store=True)


class ProductUktZed(models.Model):
    _inherit = 'product.product'

    ukt_zed = fields.Char(string='Kod UKT ZED',
                          help="Kod zgidno UKT ZED",
                          size=10)
