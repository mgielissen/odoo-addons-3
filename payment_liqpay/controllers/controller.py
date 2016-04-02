# -*- coding: utf-8 -*-

import datetime
import json
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import base64
import hashlib

_logger = logging.getLogger(__name__)


class LiqPayController(http.Controller):
    @http.route([
        '/payment/liqpay/callback',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def liqpay_callback(self, **post):
        def str_to_sign(str):
            return base64.b64encode(hashlib.sha1(str).digest())

        data = post.get('data')
        signature = post.get('signature')

        if data is None:
            _logger.warning('No data in callback')
            return 'not ok'
        if signature is None:
            _logger.warning('No signature in callback')
            return 'not ok'

        try:
            decoded_data = base64.b64decode(data)
        except TypeError:
            _logger.warning('Can not decode received data')
            return 'not ok'
        try:
            recvd_data = json.loads(decoded_data)
        except TypeError:
            _logger.warning('Can not parse received json request')
            return 'not ok'

        _logger.info('Received data: %s' % pprint.pformat(recvd_data))

        aq_id = request.registry['payment.acquirer'].search(
            request.cr,
            SUPERUSER_ID,
            [('provider', '=', 'liqpay')], limit=1, context=request.context)
        if aq_id is None:
            _logger.warning('Can not find liqpay acquirer id')
            return 'not ok'
        liqpay_aq = request.registry['payment.acquirer'].browse(
            request.cr,
            SUPERUSER_ID,
            aq_id,
            context=request.context)

        private_key = liqpay_aq.liqpay_private_key
        public_key = liqpay_aq.liqpay_public_key
        recvd_pub_key = recvd_data.get('public_key', '')

        if public_key != recvd_pub_key:
            _logger.warning('Received wrong public key: %s' % recvd_pub_key)
            return 'not ok'

        generated_sign = str_to_sign(
            private_key + data + private_key)

        if generated_sign != signature:
            _logger.warning('Received wrong signature: %s' % signature)
            return 'not ok'

        tr_ids = request.registry['payment.transaction'].search(
            request.cr,
            SUPERUSER_ID,
            [('acquirer_id', 'in', aq_id)],
            context=request.context)

        action = recvd_data.get('action', '')
        if action != 'pay' or action != 'paysplit':
            _logger.warning('Received wrong action: %s' % action)
            return 'not ok'

        order_id = recvd_data.get('order_id', '')
        status = recvd_data.get('status', '')
        acquirer_reference = recvd_data.get('payment_id', '')
        found = False

        for tr_id in tr_ids:
            tr = request.registry['payment.transaction'].browse(
                request.cr,
                SUPERUSER_ID,
                tr_id,
                context=request.context)

            if (tr.reference == order_id) and not found:
                found = True
                _logger.info('Received callback for order: %s' % order_id)
                _logger.info('Received status is: %s' % status)

                pending_statuses = ['processing',
                                    'wait_bitcoin',
                                    'wait_secure',
                                    'wait_accept',
                                    'wait_lc',
                                    'hold_wait',
                                    'hold_wait',
                                    'wait_qr',
                                    'wait_sender']
                succes_statuses = ['success',
                                   'sandbox']
                error_statuses = ['error',
                                  'failure']
                if status in pending_statuses:
                    tr.write({
                        'state': 'pending',
                        'acquirer_reference': acquirer_reference,
                    })
                if status in succes_statuses:
                    desc = recvd_data.get('description', '')
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    completion_date = recvd_data.get(
                        'completion_date',
                        now)
                    odoo_completion_date = datetime.datetime.strptime(
                        completion_date,
                        '%Y-%m-%d %H:%M:%S').strftime(
                            DEFAULT_SERVER_DATE_FORMAT)
                    _logger.info('Compl date is: %s' % completion_date)
                    tr.write({
                        'state': 'done',
                        'acquirer_reference': acquirer_reference,
                        'date_validate': odoo_completion_date,
                        'state_message': desc,
                    })
                    if tr.sale_order_id:
                        tr.sale_order_id.with_context(dict(
                            request.context,
                            send_email=True)).action_confirm()
                if status in error_statuses:
                    err_desc = recvd_data.get(
                        'err_description',
                        'error')
                    tr.write({
                        'state': 'error',
                        'acquirer_reference': acquirer_reference,
                        'state_message': err_desc,
                    })
                break
        if not found:
            _logger.warning('Received unknown transaction: %s' % order_id)
        return 'ok'
