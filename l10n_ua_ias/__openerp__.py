# -*- coding: utf-8 -*-
{
    'name': "Ukraine - Accounting",

    'summary': """Український бухоблік згідно МСФО""",

    'description': """
        Цей модуль дає можливість вести бухгалтерський
        облік діяльності підприємства згідно міжнародних
        стандартів фінансової звітності.
    """,

    'author': "ТОВ Поліс-Ч",
    'website': "https://polis-ch.ddns.ukrtel.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/
    # base/module/module_data.xml
    # for the full list
    'category': 'Localization/Account Charts',
    'version': '0.1',
    'price': 200.00,
    'currency': 'UAH',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'partner_view.xml',
        'data/account_chart_template.xml',
        'data/account.account.template.csv',
        'data/account_tax_template.xml',
        'data/account_chart_template_config.xml',
        'data/account_chart_template.yml',
    ],
    'installable': True,
}
