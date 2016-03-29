# -*- coding: utf-8 -*-

{
    'name': 'LiqPay Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: LiqPay Implementation',
    'version': '1.0',
    'description': """LiqPay Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/liqpay.xml',
        'views/payment_liqpay.xml',
        'data/liqpay.xml',
    ],
    'installable': True,
}
