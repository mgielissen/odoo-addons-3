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

    use_psp = fields.Boolean(string=u"Використовувати ПСП",
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
# TODO: move use_psp to contract
#       create index class (date, percent_amount)
#       create indexation computation function in contract


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

    @api.depends('date_from')
    def _compute_last_day(self):
        for record in self:
            if record.date_from:
                record.last_day = str(fields.Date.from_string(
                    record.date_from) + relativedelta.relativedelta(
                    months=+1, day=1, days=-1))[:10]

    @api.depends('worked_days_line_ids')
    def _compute_monthly_due(self):
        w100_d = sc_d = si_d = vp_d = sk_d = 0
        w100_h = sc_h = si_h = vp_h = sk_h = 0
        for rec in self:
            if rec.contract_id:
                lines = rec.get_worked_day_lines(rec.contract_id.id,
                                                 rec.date_from,
                                                 rec.last_day)
                for l in lines:
                    if l['code'] == 'WORK100':
                        w100_d = l['number_of_days']
                        w100_h = l['number_of_hours']
                    if l['code'] == 'SV':
                        sv_d = l['number_of_days']
                        sv_h = l['number_of_hours']
                    if l['code'] == 'SC':
                        sc_d = l['number_of_days']
                        sc_h = l['number_of_hours']
                    if l['code'] == 'SI':
                        si_d = l['number_of_days']
                        si_h = l['number_of_hours']
                    if l['code'] == 'VP':
                        vp_d = l['number_of_days']
                        vp_h = l['number_of_hours']
                    if l['code'] == 'SK':
                        sk_d = l['number_of_days']
                        sk_h = l['number_of_hours']
                rec.monthly_days = w100_d + sc_d + si_d + vp_d + sk_d
                rec.monthly_hours = w100_h + sc_h + si_h + vp_h + sk_h
