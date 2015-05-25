# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'company_registry' : fields.char('ЕДРПОУ', size=10, help='Код організації в ЕДРПОУ або код в ДРФО для фізичної особи'),
    }

    def vat_change(self, cr, uid, ids, value, context=None):
        return {'value': {'vat_subjected': bool(value)}}

    
res_partner()