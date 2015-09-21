# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class ProductTemplUktZed(models.Model):
    _inherit = 'product.template'

    ukt_zed = fields.Char(related='product_variant_ids.ukt_zed',
                          string=u"Код УКТ ЗЕД",
                          help=u"Код згідно УКТ ЗЕД",
                          store=True)


class ProductUktZed(models.Model):
    _inherit = 'product.product'

    ukt_zed = fields.Char(string=u"Код УКТ ЗЕД",
                          help=u"Код згідно УКТ ЗЕД",
                          size=10)


class ProductUomCode(models.Model):
    _inherit = 'product.uom'

    uom_code = fields.Char(string=u"Код одиниць виміру",
                           help=u"Код згідно КСПОВО",
                           size=4)
# TODO Char to integer.  <field name="uom_code" digits="[42, 5]"/>
