# -*- coding: utf-8 -*-

{
    'name': 'LiqPay Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: LiqPay Implementation',
    'version': '1.1',
    'author': "Bohdan Lisnenko",
    'website': "https://erp.co.ua",
    'description': """LiqPay Payment Acquirer""",
    'depends': ['payment', 'website_sale'],
    'data': [
        'views/liqpay.xml',
        'views/payment_liqpay.xml',
        'data/liqpay.xml',
    ],
    'installable': True,
}
