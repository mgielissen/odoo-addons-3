# -*- coding: utf-8 -*-

import json
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import hashlib

_logger = logging.getLogger(__name__)


class LiqPayController(http.Controller):
    _return_url = '/payment/liqpay/return/'
    _callback_url = '/payment/liqpay/callback/'

    @http.route([
        '/payment/liqpay/return',
    ], type='http', auth='none', csrf=False)
    def liqpay_return(self, **post):
        # TODO: reder some success text
        return werkzeug.utils.redirect('/')

    @http.route([
        '/payment/liqpay/callback',
    ], type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def liqpay_callback(self, **post):
        def str_to_sign(str):
            return base64.b64encode(hashlib.sha1(str).digest())
        data = post.get('data')
        signature = post.get('signature')
        print data
        print signature

        if data is None:
            _logger.warning('No data in callback')
            print 'no data'
            return
        if signature is None:
            _logger.warning('No signature in callback')
            print 'no signature'
            return
        tr_ids = request.registry['payment.transaction'].search(
            request.cr,
            SUPERUSER_ID,
            # [('reference', 'in', [post.get('merchantReference')])],
            # limit=1,
            context=request.context)
        for tr in tr_ids:
            print 'checking tx %s' % tr.reference
            private_key = tr.acquirer_id and tr.acquirer_id.liqpay_private_key
            sign = str_to_sign(private_key + data + private_key)
            print 'private key %s' % private_key
            print 'signature %s' % signature
            print 'sign %s' % sign
            if private_key and sign and (signature == sign):
                print 'tx is found'
                req = json.loads(base64.b64decode(data))
                print 'recvd state is %s' % req['status']
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
                if req['status'] in pending_statuses:
                    print 'uprating state to pending'
                    tr.write({'state': 'pending'})
                if req['status'] in succes_statuses:
                    print 'uprating state to done'
                    tr.write({'state': 'done'})
                if req['status'] in error_statuses:
                    print 'uprating state to error'
                    tr.write({'state': 'error'})
                break
            else:
                print 'not this tx'
        return
