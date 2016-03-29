# -*- coding: utf-'8' "-*-"

from openerp import api, fields, models, _

# _logger = logging.getLogger(__name__)


class AcquirerLiqPay(models.Model):
    _inherit = 'payment.acquirer'

    liqpay_public_key = fields.Char(string=u"Публічний ключ LiqPay")
    liqpay_private_key = fields.Char(string=u"Приватний ключ LiqPay")

    @api.v7
    def _get_providers(self, cr, uid, context=None):
        providers = super(AcquirerLiqPay, self)._get_providers(
            cr,
            uid,
            context=context)
        providers.append(['liqpay', 'LiqPay'])
        return providers

    @api.v7
    def liqpay_get_form_action_url(self, cr, uid, id, context=None):
        return 'https://www.liqpay.com/api/3/checkout'

    @api.v7
    def liqpay_form_generate_values(self, cr, uid, id, values, context=None):
        values.update({
            'liqpay_data': 'huyata ',
            'liqpay_signature': 'husignature ',
            'feedback_url': 'http://127.1:8070/payment/liqpay/callback'
        })
        return values
