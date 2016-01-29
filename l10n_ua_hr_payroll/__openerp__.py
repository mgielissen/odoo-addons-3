# -*- encoding: utf-8 -*-
{
    'name': 'Ukraine - Payroll',
    'author': "Bohdan Lisnenko",
    'website': "https://erp.co.ua",
    'category': 'Localization',
    'depends': ['hr_payroll', 'hr_holidays'],
    'version': '1.0',
    'description': """
Заробітна плата для України.
=============================

    * Оклад по днях
    * Тариф по годинах
    * Розрахунок індексації
    * Надбавки фіксовані та відсотком
    * Розрахунок утримань
    * Податкова соціальна пільга
    * ЕСВ на різницю між окладом та МЗП
    * Облік робочого часу: свята, відпустки, лікарняні, прогули.
    * Та багато іншого
    """,

    'auto_install': False,
    # 'demo': ['l10n_be_hr_payroll_demo.xml'],
    # 'website': 'https://www.odoo.com/page/accounting',
    'data': [
        'security/ir.model.access.csv',
        'data/leave_types.xml',
        'data/salary_rules_category.xml',
        'data/salary_rules.xml',
        'data/payroll_structure.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payslip_vew.xml',
        'views/hr_payroll_view.xml',
        # 'l10n_be_hr_payroll_view.xml',
        # 'l10n_be_hr_payroll_data.xml',
        # 'data/hr.salary.rule.csv',
    ],
    'installable': True
}
