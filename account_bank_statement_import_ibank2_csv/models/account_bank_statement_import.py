# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import csv


class iBank2_csv_AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'


def _parse_file(self, data_file):
    super(
     iBank2_csv_AccountBankStatementImport, self)._prepare_account_move_line(
        data_file)
