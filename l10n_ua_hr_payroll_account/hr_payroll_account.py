# -*- coding: utf-'8' "-*-"

import time
from datetime import date, datetime, timedelta

from openerp import api
from openerp.osv import fields, osv
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError


class hr_payslip_line(osv.osv):

    '''
    Payslip Line
    '''
    _inherit = 'hr.payslip.line'

    def _get_partner_id(self,
                        cr,
                        uid,
                        payslip_line,
                        credit_account,
                        context=None):
        """
        Get partner_id of slip line to use in account_move_line
        """
        # use partner of salary rule or fallback on employee's address
        partner_id = payslip_line.salary_rule_id.register_id.partner_id.id or \
            payslip_line.slip_id.employee_id.address_home_id.id
        if credit_account:
            if payslip_line.salary_rule_id.register_id.partner_id or \
                    payslip_line.salary_rule_id.account_credit.internal_type \
                    in ('receivable', 'payable'):
                return partner_id
        else:
            if payslip_line.salary_rule_id.register_id.partner_id and \
                    payslip_line.salary_rule_id.account_debit.internal_type \
                    in ('receivable', 'payable'):
                return payslip_line.slip_id.employee_id.address_home_id.id
        return False


class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    def process_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        hr_payslip_line_pool = self.pool['hr.payslip.line']
        precision = self.pool.get(
            'decimal.precision').precision_get(cr, uid, 'Payroll')
        timenow = time.strftime('%Y-%m-%d')

        for slip in self.browse(cr, uid, ids, context=context):
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to or timenow

            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            for line in slip.details_by_salary_rule_category:
                amt = slip.credit_note and -line.total or line.total
                if float_is_zero(amt, precision_digits=precision):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': hr_payslip_line_pool._get_partner_id(
                            cr,
                            uid,
                            line,
                            credit_account=False,
                            context=context),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amt > 0.0 and amt or 0.0,
                        'credit': amt < 0.0 and -amt or 0.0,
                        'analytic_account_id':
                            (line.salary_rule_id.analytic_account_id and
                                line.salary_rule_id.analytic_account_id.id or
                                False),
                        'tax_line_id':
                            (line.salary_rule_id.account_tax_id and
                                line.salary_rule_id.account_tax_id.id or
                                False),
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - \
                        debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': hr_payslip_line_pool._get_partner_id(
                            cr,
                            uid,
                            line,
                            credit_account=True,
                            context=context),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amt < 0.0 and -amt or 0.0,
                        'credit': amt > 0.0 and amt or 0.0,
                        'analytic_account_id': False,
                        'tax_line_id':
                            (line.salary_rule_id.account_tax_id and
                                line.salary_rule_id.account_tax_id.id or
                                False),
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - \
                        credit_line[2]['debit']

            if float_compare(
                    credit_sum,
                    debit_sum,
                    precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise UserError(
                        _('The Expense Journal "%s" has not ' +
                            'properly configured the Credit Account!') % (
                                slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(
                    debit_sum,
                    credit_sum,
                    precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise UserError(
                        _('The Expense Journal "%s" has not ' +
                            'properly configured the Debit Account!') % (
                                slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)

            move.update({'line_ids': line_ids})
            move_id = move_pool.create(cr, uid, move, context=context)
            self.write(
                cr,
                uid,
                [slip.id],
                {'move_id': move_id, 'date': date},
                context=context)
            move_pool.post(cr, uid, [move_id], context=context)
        return self.write(
                cr,
                uid,
                ids,
                {'paid': True, 'state': 'done'},
                context=context)
