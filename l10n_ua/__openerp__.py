# -*- coding: utf-8 -*-
{
    'name': "Українська локалізація odoo",

    'summary': """Українська локалізація odoo""",

    'description': """
        Українська локалізація odoo для:
            - модуля partner
            - модуля бух обліку
            - ...
            - profit
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
        'partner_view.xml',
        'data/account.account.type.csv',
        'data/account.account.template.csv',
        'data/account.tax.code.template.csv',
        'data/account.chart.template.csv',
        'data/account.tax.template.csv',
        'l10n_ua_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'installable': True,
}

