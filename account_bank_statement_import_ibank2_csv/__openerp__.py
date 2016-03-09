# -*- coding: utf-8 -*-
{
    'name': 'Account Bank Statement Import',
    'author': 'Bohdan Lisnenko',
    'website': 'https://erp.co.ua',
    'summary': u"Імпорт виписки у форматі iBank2 csv",
    'category': 'Accounting & Finance',
    'depends': ['account'],
    'version': '1.0',
    'description': """
Помічник імпорту банківської виписки з файлу
у форматі iBank2 csv.
Цей формат вивантаження виписки є у багатьох банках України
де використовується клієнт-банк iBank2.
""",
    'auto_install': False,
    'demo': [],
    'data': ['views/account_bank_statement_import_view.xml'],
    'installable': True
}
