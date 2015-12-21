# -*- encoding: utf-8 -*-
{
    'name': 'Ukraine - Payroll',
    'category': 'Localization',
    'depends': ['hr_payroll', 'hr_holidays'],
    'version': '1.0',
    'description': """
Ukrainian Payroll Rules.
========================

    * Employee Details
    * Employee Contracts
    * Passport based Contract
    * Allowances/Deductions
    * Allow to configure Basic/Gross/Net Salary
    * Employee Payslip
    * Monthly Payroll Register
    * Integrated with Holiday Management
    * Salary Maj, ONSS, Withholding Tax, Child Allowance, ...
    """,

    'auto_install': False,
    # 'demo': ['l10n_be_hr_payroll_demo.xml'],
    # 'website': 'https://www.odoo.com/page/accounting',
    'data': [
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
