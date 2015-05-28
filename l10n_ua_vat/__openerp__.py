# -*- coding: utf-8 -*-
{
    'name': "Ukraine - Accounting VAT support",

    'summary': """Облік ПДВ для України""",

    'description': """
        Цей модуль дає можливість вести облік виданих та отриманих податкових накладних.
    """,

    'author': "ТОВ Поліс-Ч",
    'website': "https://polis-ch.ddns.ukrtel.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization/Account Charts',
    'version': '0.1',
    'price': 200.00,
    'currency': 'EUR',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_chart'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'account_tax_invoice_view.xml',
        'account_spr_sti_view.xml',
        'company_view.xml',
        'data/account.sprsti.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'installable': True,
}

