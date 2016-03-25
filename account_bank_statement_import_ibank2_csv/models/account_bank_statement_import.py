# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import csv
from datetime import datetime
import hashlib

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class iBank2_csv_AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _parse_file(self, data_file):

        def reencode(file):
            for line in file:
                yield line.decode('windows-1251').encode('utf-8')

        sttmnt_rows = csv.reader(
            StringIO(data_file),
            delimiter=';',
            quotechar='"')

        first_row = True
        ind = {}
        columns_found = 0
        st_currency = ''
        st_account = ''
        st_data = []

        for row in sttmnt_rows:
            if first_row is True:   # first row contains column names
                first_row = False
                i = 0
                for col in row:    # find column indexes
                    dcol = col.decode('windows-1251')  # .encode('utf-8')
                    if dcol == u'ЄДРПОУ':
                        ind['EDRPOU'] = i
                        columns_found += 1
                    if dcol == u'МФО':
                        ind['MFO'] = i
                        columns_found += 1
                    if dcol == u'Рахунок':
                        ind['Account'] = i
                        columns_found += 1
                    if dcol == u'Валюта':
                        ind['Currency'] = i
                        columns_found += 1
                    if dcol == u'Дата операцiї':
                        ind['Date'] = i
                        columns_found += 1
                    if dcol == u'Код операцiї':
                        ind['ID'] = i
                        columns_found += 1
                    if dcol == u'МФО банка':
                        ind['PartMFO'] = i
                        columns_found += 1
                    if dcol == u'Назва банка':
                        ind['PartBnkName'] = i
                        columns_found += 1
                    if dcol == u'Рахунок кореспондента':
                        ind['PartAccount'] = i
                        columns_found += 1
                    if dcol == u'ЄДРПОУ кореспондента':
                        ind['PartEDRPOU'] = i
                        columns_found += 1
                    if dcol == u'Кореспондент':
                        ind['PartName'] = i
                        columns_found += 1
                    if dcol == u'Номер документа':
                        ind['DocNumber'] = i
                        columns_found += 1
                    if dcol == u'Дата документа':
                        ind['DocDate'] = i
                        columns_found += 1
                    if dcol == u'Дебет':
                        ind['Debit'] = i
                        columns_found += 1
                    if dcol == u'Кредит':
                        ind['Credit'] = i
                        columns_found += 1
                    if dcol == u'Призначення платежу':
                        ind['Memo'] = i
                        columns_found += 1
                    if dcol == u'Гривневе покриття':
                        ind['AmountUAH'] = i
                        columns_found += 1
                    i += 1
            else:    # not first row
                if columns_found != 17:
                    return super(
                        iBank2_csv_AccountBankStatementImport,
                        self)._parse_file(
                        data_file)
                if st_currency == '':
                    st_currency = row[ind['Currency']].decode(
                        'windows-1251')    # single cur for sttmnt
                if st_account == '':
                    st_account = row[ind['Account']].decode(
                        'windows-1251')    # single acc for sttmnt
                dt_date = datetime.strptime(
                    row[ind['Date']].decode('windows-1251'),
                    '%d.%m.%Y %H:%M')
                date_str = dt_date.strftime('%Y-%m-%d')

                if not any(d.get('date', None) == date_str for d in st_data):
                    # does not exist, create one
                    st_data.append({
                     'name': dt_date.strftime('%d.%m.%Y') + '/' + st_account,
                     'date': date_str,
                     'transactions': [],
                    })
                for d in st_data:
                    if d['date'] == date_str:
                        unique_str = '-'.join(row)
                        hash_obj = hashlib.md5(unique_str)
                        hash_str = hash_obj.hexdigest()

                        if row[ind['Debit']] != '':
                            amount = -1.0 * float(
                                row[ind['Debit']].decode('windows-1251'))
                        else:
                            amount = float(
                                row[ind['Credit']].decode('windows-1251'))

                        d['transactions'].append({
                            'name': row[ind['Memo']].decode('windows-1251'),
                            'date': date_str,
                            'amount': amount,
                            'unique_import_id': hash_str,
                            'account_number': row[ind['PartAccount']].decode(
                                'windows-1251'),
                            'partner_name': row[ind['PartName']].decode(
                                'windows-1251'),
                            'ref': row[ind['DocNumber']].decode(
                                'windows-1251'),
                            'note': row[ind['AmountUAH']].decode(
                                'windows-1251'),
                        })
        return st_currency, st_account, st_data
