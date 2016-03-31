# -*- coding: utf-'8' "-*-"

from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging
import urlparse
import base64
import hashlib
import json

_logger = logging.getLogger(__name__)


class AcquirerLiqPay(osv.Model):
    _inherit = 'payment.acquirer'

    _columns = {
        'liqpay_public_key': fields.char('Liqpay Public Key',
                                         required_if_provider='liqpay'),
        'liqpay_private_key': fields.char('Liqpay Private Key',
                                          required_if_provider='liqpay'),
    }

    def _get_providers(self, cr, uid, context=None):
        providers = super(AcquirerLiqPay, self)._get_providers(
            cr,
            uid,
            context=context)
        providers.append(['liqpay', 'LiqPay'])
        return providers

    def liqpay_get_form_action_url(self, cr, uid, id, context=None):
        return 'https://www.liqpay.com/api/3/checkout'

    def _make_signature(self, *args):
        def to_unicode(s):
            """
            :param s:
            :return: unicode value (decoded utf-8)
            """
            if isinstance(s, unicode):
                return s
            if isinstance(s, basestring):
                return s.decode('utf-8', 'strict')
            if hasattr(s, '__unicode__'):
                return s.__unicode__()
            return unicode(bytes(s), 'utf-8', 'strict')

        def smart_str(x):
            return to_unicode(x).encode('utf-8')

        joined_fields = ''.join(smart_str(x) for x in args)
        return base64.b64encode(hashlib.sha1(joined_fields).digest())

    def liqpay_form_generate_values(self, cr, uid, id, values, context=None):
        acquirer = self.browse(cr, uid, id, context=context)
        base_url = self.pool['ir.config_parameter'].get_param(
            cr,
            uid,
            'web.base.url')
        return_url = '%s' % urlparse.urljoin(
            base_url, '/payment/liqpay/return')
        callback_url = '%s' % urlparse.urljoin(
            base_url, '/payment/liqpay/callback')
        request = {
          'version': '3',
          'public_key': acquirer.liqpay_public_key,
          'action': 'pay',
          'amount': values['amount'],
          'currency': values['currency'] and values['currency'].name or 'UAH',
          'description': 'Order payment. Transaction %s' % values['reference'],
          'order_id': values['reference'],
          'sandbox': '1' if acquirer.environment == 'test' else '',
          'server_url': callback_url,
          'result_url': return_url,
          'sender_first_name': values['billing_partner_name'] or '',
          'sender_city': values['billing_partner_city'] or '',
          'sender_address': values['billing_partner_address'] or '',
          'sender_postal_code': values['billing_partner_zip'] or '',
        }
        data = base64.b64encode(json.dumps(request))
        signature = self._make_signature(
            acquirer.liqpay_private_key,
            json.dumps(request),
            acquirer.liqpay_private_key)
        values.update({
            'liqpay_data': data,
            'liqpay_signature': signature,
            'feedback_url': 'http://127.1:8070/payment/liqpay/callback'
        })
        return values
