# -*- coding: utf-8 -*-
{
    'name': 'Ukrainian - Payroll with Accounting',
    'author': "Bohdan Lisnenko",
    'website': "https://erp.co.ua",
    'category': 'Localization',
    'depends': ['l10n_ua_hr_payroll', 'hr_payroll_account', 'l10n_ua'],
    'version': '1.1',
    'description': """
Бухгалтерські проведення для зарплати (МСФЗ)
==============================================
    """,

    'auto_install': True,
    # 'website': 'https://www.odoo.com/page/accounting',
    'demo': [],
    'data': [
        'l10n_ua_hr_payroll_account_data.xml',
    ],
    # 'post_init_hook': '_set_accounts',
    'installable': True
}
