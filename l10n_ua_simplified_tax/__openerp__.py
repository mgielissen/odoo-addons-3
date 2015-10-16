# -*- coding: utf-8 -*-
{
    'name': u"Ukraine - Simplified Tax System",
    'summary': u"Спрощена система оподаткування",
    'description': u"""
Спрощена система оподаткування
==============================

Цей модуль створює додаткові налаштування
для ведення бухобліку за спрощеною системою оподаткування.

Після установки даного модуля буде створено нові типи податків
для спрощеної системи, які можна буде нараховувати касовим методом.

До будь-якого рядка банківської виписки можна буде призначити податок,
що призведе до збільшення бази цього податку у книзі доходів (і витрат).
    """,
    'author': "Bogdan Lisnenko",
    'category': 'Localization/Account Charts',
    'version': '1.1',
    'depends': ['account', 'account_tax_cash_basis', 'l10n_ua'],
    'data': [
        'data/simplified_tax_configuration.xml',
    ],
    'installable': True,
    'auto_install': False,
}
