# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp import SUPERUSER_ID


class weche_Event(models.Model):
    _inherit = 'event.event'

    def google_map_img(
            self,
            cr,
            uid,
            ids,
            zoom=17,
            width=298,
            height=298,
            context=None):
        event = self.browse(cr, uid, ids[0], context=context)
        if event.address_id:
            return self.browse(
                cr,
                SUPERUSER_ID,
                ids[0],
                context=context).address_id.google_map_img(
                    zoom=zoom,
                    width=width,
                    height=height)
        return None

    def google_map_link(self, cr, uid, ids, zoom=8, context=None):
        event = self.browse(cr, uid, ids[0], context=context)
        if event.address_id:
            return self.browse(
                cr,
                SUPERUSER_ID,
                ids[0],
                context=context).address_id.google_map_link(zoom=zoom)
        return None
