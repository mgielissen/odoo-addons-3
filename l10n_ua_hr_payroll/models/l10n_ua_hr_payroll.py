# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta


class HrEmployeeL10nUa(models.Model):
    _inherit = 'hr.employee'

    disable = fields.Boolean(string=u"Інвалід",
                             help=u"Податкова соціальна пільга",
                             default=False)


class HrContractL10nUa(models.Model):
    _inherit = 'hr.contract'

    bonus_fix = fields.Float(
        string=u"Фіксована надбавка",
        default=0.0,
        digits_compute=dp.get_precision('Payroll'))
    bonus_perc = fields.Float(
        string=u"Надбавка відсотком",
        default=0.0)
    use_psp = fields.Boolean(string=u"Використовувати ПСП",
                             help=u"Податкова соціальна пільга",
                             default=False)
    base_period = fields.Date(string=u"Базовий період",
                              required=True)
    index_fix = fields.Float(
        string=u"Індексація фіксована",
        default=0.0,
        digits_compute=dp.get_precision('Payroll'))
    ensurance_exp = fields.Selection([
        (50, u"50% - До 3 років"),
        (60, u"60% - Від 3 до 5 років"),
        (70, u"70% - Від 5 до 8 років"),
        (100, u"100% - Понад 8 років"),
        ],
        string=u"Страховий стаж",
        index=True,
        readonly=False,
        default=50,
        copy=False)


class HrPayslipL10nUa(models.Model):
    _inherit = 'hr.payslip'

    last_day = fields.Date(
        string=u"Останній день місяця",
        compute='_compute_last_day',
        store=True,
        default=lambda *a: str(datetime.now() + relativedelta.relativedelta(
            months=+1, day=1, days=-1))[:10])
    monthly_days = fields.Integer(string=u"Місячна норма робочих днів",
                                  compute='_compute_monthly_due',
                                  default=0,
                                  store=True)
    monthly_hours = fields.Integer(string=u"Місячна норма робочих годин",
                                   compute='_compute_monthly_due',
                                   default=0,
                                   store=True)
    indexation_coef = fields.Float(string=u"Коефіцієнт індексації ЗП",
                                   compute='_compute_indexation_coef',
                                   default=0.00,
                                   digits=(4, 1),
                                   store=True)
    january_mzp = fields.Float(string=u"МЗП на 1 січня",
                               compute='_compute_january_mzp',
                               default=0.00,
                               digits=(7, 2),
                               store=True)
    january_mzp_hr = fields.Float(
        string=u"МЗП год. на 1 січня",
        compute='_compute_january_mzp',
        default=0.00,
        digits=(7, 2),
        store=True)
    current_mzp = fields.Float(string=u"МЗП поточна",
                               compute='_compute_current_mzp',
                               default=0.00,
                               digits=(7, 2),
                               store=True)
    current_mzp_hr = fields.Float(
        string=u"МЗП год. поточна",
        compute='_compute_current_mzp',
        default=0.00,
        digits=(7, 2),
        store=True)
    comp_start_day = fields.Date(
        string=u"Перший день для розрах комп.",
        compute='_compute_comp_days',
        store=True)
    comp_last_day = fields.Date(
        string=u"Останній день для розрах комп.",
        compute='_compute_comp_days',
        store=True)
    comp_numb_days = fields.Float(
        string=u"Кількість календарних днів у місяці розрахунку",
        compute='_compute_comp_days',
        default=0.00,
        digits=(7, 2),
        store=True)

    @api.model
    def get_worked_day_lines(self,
                             contract_ids,
                             date_from,
                             date_to):
        '''Temporary fix. Currently original function
        returns leaves['code'] == leaves['name']
        so we travel though leaves list and modifiy
        leaves['code'] to corrsponding code.
        Otherwise python parser will not be able
        to execute python code of salary rule.
        (code field would contain spaces from name field)'''
        res = super(HrPayslipL10nUa, self).get_worked_day_lines(contract_ids,
                                                                date_from,
                                                                date_to)
        for l in res:
            if l['code'] == 'WORK100':
                l['name'] = u"Відпрацьовано днів"
            else:
                domain = [('name', '=', l['name'])]
                leave = self.env['hr.holidays.status'].search(domain,
                                                              limit=1)
                if len(leave) > 0:
                    l['code'] = leave.code
        return res

    @api.depends('date_from', 'date_to')
    def _compute_last_day(self):
        for record in self:
            if record.date_from:
                record.last_day = str(fields.Date.from_string(
                    record.date_from) + relativedelta.relativedelta(
                    months=+1, day=1, days=-1))[:10]

    @api.depends('date_from', 'date_to')
    def _compute_comp_days(self):
        for record in self:
            if record.date_from:
                record.comp_start_day = str(fields.Date.from_string(
                    record.date_from) + relativedelta.relativedelta(
                    years=-1, day=1))[:10]
                record.comp_last_day = str(fields.Date.from_string(
                    record.date_from) + relativedelta.relativedelta(
                    day=1, days=-1))[:10]
                delta = fields.Date.from_string(
                    record.date_to) - \
                    fields.Date.from_string(
                        record.date_from)
                record.comp_numb_days = delta.days

    @api.depends('date_from', 'date_to', 'contract_id', 'last_day')
    def _compute_monthly_due(self):
        """@returns number of scheduled days
        and hours to work for this month.
        Should be equal to calendar days - holidays"""
        scheduled_days = scheduled_hours = 0
        for rec in self:
            if rec.date_from:
                first_day = fields.Date.from_string(rec.date_from)
                first_day = first_day.strftime('%Y-%m-01')
            else:
                first_day = None
            if rec.contract_id and first_day and rec.last_day:
                lines = rec.get_worked_day_lines(rec.contract_id.id,
                                                 first_day,
                                                 rec.last_day)
                for l in lines:
                    if l['code'] != 'SV':   # skip approved holidays
                        scheduled_days += l['number_of_days']
                        scheduled_hours += l['number_of_hours']
                rec.monthly_days = scheduled_days
                rec.monthly_hours = scheduled_hours

    @api.depends('date_from', 'date_to', 'contract_id')
    def _compute_indexation_coef(self):
        INDEXATION_THRESHOLD = 103.0    # поріг індексації 103% з 2016 року

        def _diff_month(d1, d2):
            return (d1.year - d2.year) * 12 + d1.month - d2.month

        for rec in self:
            if not rec.date_from or not rec.contract_id.base_period:
                rec.indexation_coef = 0.0
                continue

            base_p = fields.Date.from_string(rec.contract_id.base_period)
            base_p = datetime.strptime(
                base_p.strftime('%Y-%m-01'), '%Y-%m-%d')
            payslip_date = fields.Date.from_string(rec.date_from)
            payslip_date = datetime.strptime(
                payslip_date.strftime('%Y-%m-01'), '%Y-%m-%d')

            if _diff_month(base_p, payslip_date) > -2:
                # індексація нараховується починаючи з 4-го місяця
                rec.indexation_coef = 0.0
                continue

            ind_date_for_payslip = payslip_date + \
                relativedelta.relativedelta(months=-2)
            domain = [('date', '>', base_p),
                      ('date', '<=', ind_date_for_payslip)]
            priceindexes = self.env['hr.l10n_ua_payroll.priceindex'].search(
                domain)
            coef = 100.0
            base = 100.0
            for p_ind in priceindexes:
                base = (base * p_ind.index) / 100.0
                base = round(base, 1)
                if base > INDEXATION_THRESHOLD:
                    coef = (coef * base) / 100
                    coef = round(coef, 1)
                    base = 100.0
            rec.indexation_coef = coef - 100.0

    @api.depends('date_from', 'date_to')
    def _compute_january_mzp(self):
        for record in self:
            if record.date_from:
                payslip_date = fields.Date.from_string(record.date_from)
                payslip_date = datetime.strptime(
                    payslip_date.strftime('%Y-01-01'), '%Y-%m-%d')
                domain = [('date', '=', payslip_date)]
                mzp = self.env['hr.l10n_ua_payroll.mzp'].search(domain,
                                                                limit=1)
                if len(mzp) > 0:
                    record.january_mzp = mzp.mzp
                    record.january_mzp_hr = mzp.mzp_hourly
                else:
                    record.january_mzp = 0.0
                    record.january_mzp_hr = 0.0

    @api.depends('date_from', 'date_to')
    def _compute_current_mzp(self):
        for record in self:
            if record.date_from:
                payslip_date = fields.Date.from_string(record.date_from)
                payslip_date = datetime.strptime(
                    payslip_date.strftime('%Y-%m-01'), '%Y-%m-%d')
                domain = [('date', '<=', payslip_date)]
                mzps = self.env['hr.l10n_ua_payroll.mzp'].search(domain)
                if len(mzps) > 0:
                    mzps = mzps.sorted(key=lambda r: r.date, reverse=True)
                    mzp_last = mzps[0]
                    record.current_mzp = mzp_last.mzp
                    record.current_mzp_hr = mzp_last.mzp_hourly
                else:
                    record.current_mzp = 0.0
                    record.current_mzp_hr = 0.0

    @api.onchange('date_to')
    def _onchange_dates(self):
        return self.onchange_employee_id(self.date_from,
                                         self.date_to,
                                         self.employee_id.id,
                                         self.contract_id.id)


class HrPriceIndexL10nUa(models.Model):
    _name = 'hr.l10n_ua_payroll.priceindex'
    _description = 'Index of consumer prices'

    name = fields.Char(string=u"Індекс споживчих цін",
                       readonly=True,
                       required=False,
                       default=u"Індекс споживчих цін")
    date = fields.Date(string=u"Дата",
                       required=True,
                       default=lambda *a: time.strftime('%Y-%m-01'),)
    index = fields.Float(string=u"Індекс споживчих цін",
                         default=100.0,
                         digits=(4, 1),
                         required=True)

    @api.multi
    def write(self, vals):
        if 'date' in vals:
            # ensure date is set to first day of a month
            vals['date'] = vals['date'][:7] + '-01'
        return super(HrPriceIndexL10nUa, self).write(vals)

    @api.model
    def create(self, vals):
        if 'date' in vals:
            # ensure date is set to first day of a month
            vals['date'] = vals['date'][:7] + '-01'
        return super(HrPriceIndexL10nUa, self).create(vals)


class HrMzpL10nUa(models.Model):
    _name = 'hr.l10n_ua_payroll.mzp'
    _description = 'Minimal wage'

    name = fields.Char(string=u"Мінімальна заробітна плата",
                       readonly=True,
                       required=False,
                       default=u"Мінімальна заробітна плата")
    date = fields.Date(string=u"Дата",
                       required=True,
                       default=lambda *a: time.strftime('%Y-%m-01'),)
    mzp = fields.Float(string=u"Мінімальна місячна заробітна плата",
                       default=0.0,
                       digits=(7, 2),
                       required=True)
    mzp_hourly = fields.Float(string=u"Мінімальна погодинна заробітна плата",
                              default=0.0,
                              digits=(7, 2),
                              required=True)

    @api.multi
    def write(self, vals):
        if 'date' in vals:
            # ensure date is set to first day of a month
            vals['date'] = vals['date'][:7] + '-01'
        return super(HrMzpL10nUa, self).write(vals)

    @api.model
    def create(self, vals):
        if 'date' in vals:
            # ensure date is set to first day of a month
            vals['date'] = vals['date'][:7] + '-01'
        return super(HrMzpL10nUa, self).create(vals)


class HolidaysStatusCodeL10nUa(models.Model):
    _inherit = 'hr.holidays.status'

    code = fields.Char(string=u"Код")
