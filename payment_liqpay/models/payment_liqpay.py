# -*- coding: utf-'8' "-*-"

from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)


class AcquirerAdyen(models.Model):
    _inherit = 'payment.acquirer'

    public_key = fields.Char(string=u"Публічний ключ")
    privat_key = fields.Char(string=u"Приватний ключ")
