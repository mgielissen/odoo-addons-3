# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


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
