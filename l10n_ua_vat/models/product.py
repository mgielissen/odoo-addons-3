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


class ProductUomCode(models.Model):
    _inherit = 'product.uom'

    uom_code = fields.Char(string='Kod odynyts vymiru',
                           help="Kod zgidno KSPOVO",
                           size=4)
# TODO Char to integer.  <field name="uom_code" digits="[42, 5]"/>
