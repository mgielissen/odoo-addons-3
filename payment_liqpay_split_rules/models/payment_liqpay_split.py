# -*- coding: utf-'8' "-*-"

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import logging
import urlparse
import base64
import hashlib
import json
import pprint

_logger = logging.getLogger(__name__)


class res_partner_split(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'liqpay_public_key': fields.char('Liqpay Public Key'),
        'liqpay_split_commision': fields.float(
                'Commision percent to shop',
                required=False,
                digits=(16, 2),
                track_visibility='always',
                help='In percent')
    }


class AcquirerLiqPaySplit(osv.Model):
    _inherit = 'payment.acquirer'

    _columns = {
        'liqpay_2nd_public_key': fields.char('Liqpay 2nd Public Key'),
        'liqpay_2nd_private_key': fields.char('Liqpay 2nd Private Key'),
    }

    def liqpay_form_generate_values(self, cr, uid, id, values, context=None):
        split = {}
        tx_obj = self.pool['payment.transaction']
        so_obj = self.pool['sale.order']
        base_url = self.pool['ir.config_parameter'].get_param(
            cr,
            uid,
            'web.base.url')
        callback_url = '%s' % urlparse.urljoin(
            base_url, '/payment/liqpay/callback')

        if values['reference'] == '/':  # zrada
            return \
             super(AcquirerLiqPaySplit, self).liqpay_form_generate_values(
                cr,
                uid,
                id,
                values,
                context=context)
        tx_id = tx_obj.search(
                            cr,
                            SUPERUSER_ID,
                            [
                                ('partner_id', '=', values['partner_id']),
                                ('amount', '=', values['amount'],),
                                ('reference', '=', values['reference'],)
                            ],
                            limit=1,
                            context=context)
        tx = tx_obj.browse(cr,
                           SUPERUSER_ID,
                           tx_id,
                           context=context)
        _logger.info('Found tx: %s' % tx.reference)

        if not tx.sale_order_id:    # zrada
            return \
             super(AcquirerLiqPaySplit, self).liqpay_form_generate_values(
                cr,
                uid,
                id,
                values,
                context=context)

        my_amount = values['amount']
        for line in tx.sale_order_id.order_line:
            if line.product_id.event_ok:
                ticket = line.event_ticket_id
                if ticket:
                    org = ticket.event_id.organizer_id
                    if org and \
                       org.liqpay_public_key != '' and \
                       org.liqpay_split_commision and \
                       org.liqpay_split_commision != 0:
                        perc = 100 - org.liqpay_split_commision
                        amount = round(line.price_total * perc / 100, 2)
                        my_amount -= amount
                        key = org.id
                        if key in split:
                            split[key]['amount'] += amount
                        else:
                            split[key] = {
                                'public_key': org.liqpay_public_key,
                                'amount': amount,
                                'commission_payer': 'receiver',
                                'server_url': callback_url
                            }
                        _logger.info('Organizer: %s' % org.name)
                        _logger.info('Ticket name: %s' % ticket.name)
                        _logger.info(' subtotal: %s' % line.price_subtotal)
                        _logger.info(' tax: %s' % line.price_tax)
                        _logger.info(' total: %s' % line.price_total)
                        _logger.info(' perc: %s' % perc)
                        _logger.info(' amount: %s' % amount)
                        _logger.info('-----------')

        sum_amnt = 0
        my_amount = round(my_amount, 2)
        for k in split:
            sum_amnt += split[k]['amount']
        delta = values['amount'] - sum_amnt - my_amount
        if delta != 0:
            my_amount += delta
        split['my'] = {
            'public_key': tx.acquirer_id.liqpay_2nd_public_key,
            'amount': my_amount,
            'commission_payer': 'receiver',
            'server_url': callback_url
        }

        split_rules = []
        for k in split:
            split_rules.append(split[k])
        values.update({
            'split_rules': split_rules
        })
        _logger.info('values: %s' % pprint.pformat(values))
        return super(AcquirerLiqPaySplit, self).liqpay_form_generate_values(
            cr,
            uid,
            id,
            values,
            context=context)
