# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning, UserError
import openerp.addons.decimal_precision as dp


# mapping taxinvoice type to journal type
TYPE2JOURNAL = {
    'out_tax_invoice': 'sale',
    'in_tax_invoice': 'purchase',
}


class TIContrType(models.Model):
    _name = 'account.taxinvoice.contrtype'
    _description = 'Tax Invoice Contract Type'

    name = fields.Char(string=u"Тип договору")


class TIPayMeth(models.Model):
    _name = 'account.taxinvoice.paymeth'
    _description = 'Tax Invoice Payment method'

    name = fields.Char(string=u"Спосіб оплати")


class TaxInvoice(models.Model):
    _name = 'account.taxinvoice'
    _description = 'Tax Invoice'

    state = fields.Selection([
                             ('draft', u"Чорновий"),
                             ('ready', u"Підготовлено"),
                             ('sent', u"На реєстрації"),
                             ('registered', u"Зареєстровано"),
                             ('cancel', u"Скасовано"),
                             ],
                             string=u"Статус",
                             index=True,
                             readonly=True,
                             default='draft',
                             track_visibility='onchange',
                             copy=False,
                             help=" * The 'Draft' status is used when a user "
                             "is encoding a new and unconfirmed Invoice.\n"
                             " * The 'Pro-forma' status is used the invoice "
                             "does not have an invoice number.\n"
                             " * The 'Open' status is used when user create "
                             "invoice, an invoice number is generated. Its in "
                             "open status till user does not pay invoice.\n"
                             " * The 'Paid' status is set automatically when "
                             "the invoice is paid. Its related journal "
                             "entries may or may not be reconciled.\n"
                             " * The 'Cancelled' status is used when user "
                             "cancel invoice.")

    h01 = fields.Boolean(string=u"Складається інвестором",
                         default=False,
                         readonly=True,
                         states={'draft': [('readonly', False)]})
    horig1 = fields.Boolean(string=u"Не видається покупцю",
                            states={'draft': [('readonly', False)]},
                            readonly=True,
                            default=False)
    htypr = fields.Selection([
        ('00', u"Немає"),
        ('01', u"01 - "
         u"Складена на суму перевищення звичайної ціни над фактичною"),
        ('02', u"02 - "
         u"Постачання неплатнику податку"),
        ('03', u"03 - "
         u"Постачання товарів/послуг у рахунок оплати праці фізичним особам, "
         u"які перебувають у трудових відносинах із платником податку"),
        ('04', u"04 - "
         u"Постачання у межах балансу для невиробничого використання"),
        ('05', u"05 - "
         u"Ліквідація основних засобів за самостійним "
         u"рішенням платника податку"),
        ('06', u"06 - "
         u"Переведення виробничих основних засобів до складу невиробничих"),
        ('07', u"07 - "
         u"Експортні постачання"),
        ('08', u"08 - "
         u"Постачання для операцій, які не є об'єктом оподаткування "
         u"податком на додану вартість"),
        ('09', u"09 - "
         u"Постачання для операцій, які звільнені від оподаткування "
         u"податком на додану вартість"),
        ('10', u"10 - "
         u"Визначення при анулюванні платника податку податкових зобов'язань "
         u"по товарах/послугах, необоротних активах, суми податку по яких "
         u"були включені до складу податкового кредиту, не були використані "
         u"в оподатковуваних операціях у межах господарської діяльності"),
        ('11', u"11 - "
         u"Складена за щоденними підсумками операцій"),
        ('12', u"12 - "
         u"Складена на вартість безоплатно поставлених товарів/послуг, "
         u"обчислену виходячи з рівня звичайних цін"),
        ('13', u"13 - "
         u"Використання виробничих або невиробничих засобів, інших "
         u"товарів/послуг не у господарській діяльності"),
        ('14', u"14 - "
         u"Складена покупцем (отримувачем) послуг від нерезидента"),
        ('15', u"15 - "
         u"Складена на суму перевищення митної вартості над фактичною "
         u"ціною постачання"),
        ('16', u"16 - "
         u"Складена на суму перевищення балансової (залишкової) вартості "
         u"необоротних активів над фактичною ціною їх постачання"),
        ('17', u"17 - "
         u"Складена на суму перевищення собівартості самостійно виготовлених "
         u"товарів/послуг над фактичною ціною їх постачання"),
    ], string=u"Тип причини", index=True,
        change_default=True, default='00',
        states={'draft': [('readonly', False)]},
        readonly=True,
        track_visibility='always')

    date_vyp = fields.Date(
        string=u"Дата складання",
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help=u"Дата першої події з ПДВ",
        default=lambda self: fields.Date.context_today(self),
        copy=True,
        required=True)

    date_reg = fields.Date(string=u"Дата реєстрації", index=True,
                           readonly=False,
                           states={'registered': [('readonly', True)]},
                           help=u"Дата реєстрації в ЄРПН",
                           copy=False)

    number = fields.Char(string=u"Номер", size=7,
                         readonly=True,
                         states={'draft': [('readonly', False)],
                                 'ready': [('readonly', False)]},
                         required=False)
    number1 = fields.Char(string=u"Ознака спеціальної ПН",
                          states={'draft': [('readonly', False)]},
                          readonly=True,
                          size=1)
    number2 = fields.Char(string=u"Код філії",
                          states={'draft': [('readonly', False)]},
                          readonly=True,
                          size=4)

    category = fields.Selection([
        ('out_tax_invoice', u"Видані ПН"),
        ('in_tax_invoice', u"Отримані ПН"),
    ], string=u"Категорія", readonly=True,
        index=True, change_default=True,
        default=lambda self: self._context.get('category', 'out_tax_invoice'),
        track_visibility='always')

    doc_type = fields.Selection([
        ('pn', u"Податкова накладна"),
        ('rk', u"Розрахунок коригування до ПН"),
        ('vmd', u"Митна декларація"),
        ('tk', u"Транспортний квиток"),
        ('bo', u"Бухгалтерська довідка"),
    ], string=u"Тип документу", index=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
        change_default=True, default='pn',
        track_visibility='always')

    partner_id = fields.Many2one(
        'res.partner',
        string=u"Партнер", ondelete='set null',
        help=u"Компанія-партнер",
        index=True, required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[ \
                  ('supplier', \
                   { \
                     'out_tax_invoice': '<=', \
                     'in_tax_invoice': '=' \
                    }.get(category, []), \
                   'True'), \
                   ('customer', \
                    { \
                      'out_tax_invoice': '=', \
                      'in_tax_invoice': '<=' \
                     }.get(category, []), \
                    'True'), \
                ]"  # Show only customers or suppliers
    )

    ipn_partner = fields.Char(string=u"ІПН партнера",
                              states={'draft': [('readonly', False)]},
                              readonly=True,
                              required=True)
    adr_partner = fields.Char(string=u"Адреса партнера",
                              states={'draft': [('readonly', False)]},
                              readonly=True,
                              required=False)
    tel_partner = fields.Char(string=u"Телефон партнера",
                              readonly=True,
                              states={'draft': [('readonly', False)]})

    contract_type = fields.Many2one('account.taxinvoice.contrtype',
                                    string=u"Тип договору",
                                    ondelete='set null',
                                    states={'draft': [('readonly', False)]},
                                    readonly=True,
                                    help=u"Тип договору згідно ЦКУ",
                                    index=True)
    contract_date = fields.Date(string=u"Дата договору",
                                readonly=True,
                                states={'draft': [('readonly', False)]})
    contract_numb = fields.Char(string=u"Номер договору",
                                readonly=True,
                                states={'draft': [('readonly', False)]},)
    payment_meth = fields.Many2one('account.taxinvoice.paymeth',
                                   string=u"Спосіб оплати",
                                   states={'draft': [('readonly', False)]},
                                   readonly=True,
                                   ondelete='set null',
                                   help=u"Спосіб оплати за постачання",
                                   index=True)
    prych_zv = fields.Char(string=u"Причина звільнення від ПДВ",
                           states={'draft': [('readonly', False)]},
                           readonly=True,
                           required=False)
    signer_id = fields.Many2one('res.users',
                                string=u"Відповідальна особа",
                                states={'draft': [('readonly', False)]},
                                readonly=True,
                                required=False,
                                ondelete='set null',
                                help=u"Особа, яка склала і підписала ПН",
                                index=True,
                                domain="[('company_id', '=', company_id)]")

    # Modified record name on form view
    @api.multi
    def name_get(self):
        TYPES = {
            'pn': u"Податкова накладна",
            'rk': u"Розрахунок коригування до ПН",
            'vmd': u"Митна декларація",
            'tk': u"Транспортний квиток",
            'bo': u"Бухгалтерська довідка",
        }
        result = []
        for inv in self:
            date = fields.Date.from_string(inv.date_vyp)
            datef = date.strftime('%d.%m.%Y')
            result.append(
                (inv.id, u"%s № %s від %s" %
                    (TYPES[inv.doc_type], inv.number, datef)))
        return result

    @api.onchange('partner_id')
    def update_partner_info(self):
        if not self.partner_id:
            return
        else:
            self.ipn_partner = self.partner_id.vat if \
                self.partner_id.vat else ''
            self.tel_partner = self.partner_id.phone if \
                self.partner_id.phone else ''
            self.adr_partner = ''
            if self.partner_id.zip:
                self.adr_partner = self.adr_partner + self.partner_id.zip
            if self.partner_id.state_id.name:
                self.adr_partner = self.adr_partner + ', ' + \
                    self.partner_id.state_id.name
            if self.partner_id.city:
                self.adr_partner = self.adr_partner + \
                    ', ' + self.partner_id.city
            if self.partner_id.street:
                self.adr_partner = self.adr_partner + \
                    ', ' + self.partner_id.street
            if self.partner_id.street2:
                self.adr_partner = self.adr_partner + \
                    ', ' + self.partner_id.street2
        return {}

    @api.model
    def _default_journal(self):
        tinv_type = self._context.get('category', 'out_tax_invoice')
        tinv_types = tinv_type if isinstance(tinv_type, list) else [tinv_type]
        company_id = self._context.get('company_id',
                                       self.env.user.company_id.id)
        domain = [('type', 'in',
                   filter(None, map(TYPE2JOURNAL.get, tinv_types))),
                  ('company_id', '=', company_id),
                  ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.model
    def _default_account(self):
        # TODO: create res_config field and check it first
        # if not set do search on all accounts for tag
        # and store result in res_config field to avoid
        # massive search on all accounts each time
        company_id = self._context.get('company_id',
                                       self.env.user.company_id.id)
        domain = [('company_id', '=', company_id)]
        for acc in self.env['account.account'].search(domain):
            for tag in acc.tag_ids:
                if tag.name.find(u"ПДВ") >= 0:
                    return acc
        return False

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency_id or journal.company_id.currency_id

    taxinvoice_line_ids = fields.One2many('account.taxinvoice.line',
                                          'taxinvoice_id',
                                          string=u"Рядки ПН",
                                          readonly=True,
                                          states={'draft': [('readonly',
                                                             False)]},
                                          copy=True)
    tax_line_ids = fields.One2many('account.taxinvoice.tax', 'taxinvoice_id',
                                   string=u"Рядки податків",
                                   readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   copy=True)
    move_id = fields.Many2one('account.move', string=u"Запис в журналі",
                              readonly=True,
                              index=True,
                              ondelete='restrict',
                              copy=False,
                              help=u"Посилання на запис в журналі проведень")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True,
                                  readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=_default_currency,
                                  track_visibility='always')
    company_currency_id = fields.Many2one('res.currency',
                                          related='company_id.currency_id',
                                          readonly=True)
    journal_id = fields.Many2one('account.journal',
                                 string='Journal',
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=_default_journal,
                                 domain="[('type', 'in', \
                                          {'out_tax_invoice': \
                                           ['sale'], \
                                           'in_tax_invoice': \
                                           ['purchase']}.get( \
                                           category, [])), \
                                           ('company_id', '=', \
                                           company_id)]"
                                 )
    company_id = fields.Many2one(
        'res.company',
        string=u"Компанія",
        change_default=True,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: (self.env['res.company']._company_default_get(
            'account.taxinvoice')))
    account_id = fields.Many2one('account.account',
                                 string=u"Рахунок",
                                 required=True,
                                 readonly=True,
                                 default=_default_account,
                                 states={'draft': [('readonly', False)]},
                                 domain=[('deprecated', '=', False)],
                                 help=u"Рахунок розрахунків по ПДВ")
    amount_untaxed = fields.Monetary(string=u"Разом",
                                     store=True,
                                     readonly=True,
                                     compute='_compute_amount',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string=u"Податок",
                                 store=True,
                                 readonly=True,
                                 compute='_compute_amount')
    amount_total = fields.Monetary(string=u"Всього",
                                   store=True,
                                   readonly=True,
                                   compute='_compute_amount')
    amount_tara = fields.Monetary(string=u"Зворотна тара",
                                  readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=0.00)
    invoice_id = fields.Many2one('account.invoice',
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 string=u"Рахунок-фактура",
                                 copy=False,
                                 help=u"Пов’язаний рахунок",
                                 domain="[('type', 'in', \
                                          {'out_tax_invoice': \
                                           ['out_invoice'], \
                                           'in_tax_invoice': \
                                           ['in_invoice']}.get( \
                                           category, [])), \
                                           ('company_id', '=', \
                                           company_id)]")

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id.id or \
                self.journal_id.company_id.currency_id.id

    @api.onchange('taxinvoice_line_ids')
    def _onchange_taxinvoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.browse([])
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        partner = self.partner_id
        for line in self.taxinvoice_line_ids:
            if line.taxinvoice_line_tax_id:
                tl_id = line.taxinvoice_line_tax_id
                if tl_id.name.find(u"ПДВ") >= 0:
                    price_unit = line.price_unit * \
                        (1 - (line.discount or 0.0) / 100.0)

                    prec = self.currency_id.decimal_places
                    if self.company_id.tax_calculation_rounding_method == \
                       'round_globally':
                        prec += 5
                    total_excluded = total_included = base = \
                        round(price_unit * line.quantity, prec)

                    tax_amount = base * tl_id.amount / 100
                    tax_amount = self.currency_id.round(tax_amount)

                    total_included += tax_amount

                    val = {
                        'taxinvoice_id': self.id,
                        'name': tl_id.name,
                        'tax_id': tl_id.id,
                        'base': base,
                        'amount': tax_amount,
                        'manual': False,
                        'sequence': tl_id.sequence,
                        'account_analytic_id': tl_id.analytic or False,
                        'account_id': (tl_id.account_id or line.account_id.id),
                    }

                    key = tl_id.id
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
            else:
                continue
        return tax_grouped

    @api.one
    @api.depends('taxinvoice_line_ids.price_subtotal',
                 'tax_line_ids.amount',
                 'currency_id',
                 'company_id',
                 'amount_tara')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.base for line in self.tax_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.amount_total += self.amount_tara

    @api.multi
    def get_number(self):
        for tinv in self:
            if tinv.category == 'out_tax_invoice':
                if not tinv.number:
                    tinv.number = \
                        self.env['ir.sequence'].next_by_code('out.taxinvoice')
            if tinv.category == 'in_tax_invoice':
                if not tinv.number:
                    raise UserError(_(u"Вкажіть номер податкової накладної"))
        return

    @api.multi
    def action_ready(self):
        for tinv in self:
            if tinv.category == 'out_tax_invoice':
                if not tinv.taxinvoice_line_ids:
                    raise UserError(_(u"Немає жодного рядка в документі!"))
        return self.write({'state': 'ready'})

    @api.multi
    def action_sent(self):
        return self.write({'state': 'sent'})

    @api.multi
    def action_registered(self):
        for tinv in self:
            if not tinv.date_reg:
                raise UserError(_(u"Спочатку вкажіть дату реєстрації."))
        return self.write({'state': 'registered'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_move_create(self):
        """ Creates tax invoice related financial move lines """
        account_move = self.env['account.move']

        for tinv in self:
            if tinv.amount_tax == 0:
                raise UserError(_(u"0 tax"))
                return True    # no moves if taxes amount == 0
            if tinv.move_id:
                raise UserError(_(u"1"))
                continue
            if tinv.invoice_id:
                if tinv.invoice_id.number:
                    reference = tinv.invoice_id.number
                else:
                    reference = '/'
            else:
                reference = '/'
            ctx = dict(self._context, lang=tinv.partner_id.lang)
            date_taxinvoice = tinv.date_vyp
            company_currency = tinv.company_id.currency_id
            journal = tinv.journal_id.with_context(ctx)
            date = tinv.date_vyp
            move_vals = {
                'name': u"ПН/%s" % tinv.number,
                'journal_id': journal.id,
                'ref': reference,
                'date': date,
            }
            ctx['company_id'] = tinv.company_id.id
            ctx['dont_create_taxes'] = True
            ctx['check_move_validity'] = False
            move = account_move.with_context(ctx).create(move_vals)
            # one move per tax line and
            # last move in counterpart for total tax amount
            for t_line in tinv.tax_line_ids:
                if t_line.amount > 0:
                    deb = t_line.amount \
                        if (tinv.category == 'out_tax_invoice') else 0.00
                    cred = t_line.amount \
                        if (tinv.category == 'in_tax_invoice') else 0.00
                    self.env['account.move.line'].with_context(ctx).create({
                        'date_maturity': tinv.date_vyp,
                        'partner_id': tinv.partner_id.id,
                        'name': t_line.name,
                        'debit': deb,
                        'credit': cred,
                        'account_id': t_line.account_id.id,
                        'currency_id': tinv.currency_id.id,
                        'quantity': 1.00,
                        'tax_line_id': t_line.tax_id.id,
                        'analytic_line_ids': False,
                        'product_id': False,
                        'product_uom_id': False,
                        'analytic_account_id': False,
                        'invoice_id': False,
                        'tax_ids': False,
                        'move_id': move.id,
                    })
            deb = tinv.amount_tax \
                if (tinv.category == 'in_tax_invoice') else 0.00
            cred = tinv.amount_tax \
                if (tinv.category == 'out_tax_invoice') else 0.00
            self.env['account.move.line'].with_context(ctx).create({
                'date_maturity': tinv.date_vyp,
                'partner_id': tinv.partner_id.id,
                'name': u"ПН/%s" % tinv.number,
                'debit': deb,
                'credit': cred,
                'account_id': tinv.account_id.id,
                'currency_id': tinv.currency_id.id,
                'quantity': 1.00,
                'analytic_line_ids': False,
                'product_id': False,
                'product_uom_id': False,
                'analytic_account_id': False,
                'invoice_id': False,
                'tax_ids': False,
                'tax_line_id': False,
                'move_id': move.id,
            })
            move.post()
            # make the taxinvoice point to that move
            vals = {
                'move_id': move.id,
            }
            tinv.with_context(ctx).write(vals)
        return True

    @api.multi
    def _export_xml_data(self):
        """Prepare xml data for export.
        This function returns name of xml file
        and data to be put inside."""
        self.ensure_one()
        if not self.company_id.comp_sti:
            raise UserError(_(u"Вкажіть вашу ДПІ у налаштуваннях компанії."))
        if not self.company_id.company_registry:
            raise UserError(_(u"Вкажіть ІПН у налаштуваннях компанії."))

        date = fields.Date.from_string(self.date_vyp)
        # compose file name
        fname = ''
        fname = self.company_id.comp_sti.c_sti
        fname += self.company_id.company_registry.zfill(10)
        fname += 'J12'
        fname += '010'
        fname += '07'
        fname += '1'
        fname += '00'
        fname += self.number.zfill(7)
        fname += '1'
        fname += date.strftime('%m')
        fname += date.strftime('%Y')
        fname += self.company_id.comp_sti.c_sti
        fname += '.xml'
        declar = ET.Element('DECLAR')
        declar.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        declar.set('xsi:noNamespaceSchemaLocation', 'J1201007.xsd')
        declarhead = ET.SubElement(declar, 'DECLARHEAD')
        # declarhead part
        ET.SubElement(declarhead, 'TIN').text = \
            self.company_id.company_registry
        ET.SubElement(declarhead, 'C_DOC').text = 'J12'
        ET.SubElement(declarhead, 'C_DOC_SUB').text = '010'
        ET.SubElement(declarhead, 'C_DOC_VER').text = '7'
        ET.SubElement(declarhead, 'C_DOC_TYPE').text = '0'
        ET.SubElement(declarhead, 'C_DOC_CNT').text = self.number
        ET.SubElement(declarhead, 'C_REG').text = \
            self.company_id.comp_sti.c_sti[0:2]
        ET.SubElement(declarhead, 'C_RAJ').text = \
            self.company_id.comp_sti.c_raj
        ET.SubElement(declarhead, 'PERIOD_MONTH').text = date.strftime('%m')
        ET.SubElement(declarhead, 'PERIOD_TYPE').text = '1'
        ET.SubElement(declarhead, 'PERIOD_YEAR').text = date.strftime('%Y')
        ET.SubElement(declarhead, 'C_STI_ORIG').text = \
            self.company_id.comp_sti.c_sti
        ET.SubElement(declarhead, 'C_DOC_STAN').text = '1'
        ET.SubElement(declarhead, 'LINKED_DOCS').set('xsi:nil', 'true')
        ET.SubElement(declarhead, 'D_FILL').text = date.strftime('%d%m%Y')
        ET.SubElement(declarhead, 'SOFTWARE').text = 'Odoo 9'
        # declarbody part
        declarbody = ET.SubElement(declar, 'DECLARBODY')
        if self.h01:
            ET.SubElement(declarbody, 'H01').text = '1'
        else:
            ET.SubElement(declarbody, 'H01').set('xsi:nil', 'true')
        if self.horig1:
            ET.SubElement(declarbody, 'HORIG1').text = '1'
            ET.SubElement(declarbody, 'HTYPR').text = self.htypr
        else:
            ET.SubElement(declarbody, 'HORIG1').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'HTYPR').set('xsi:nil', 'true')
        ET.SubElement(declarbody, 'HFILL').text = date.strftime('%d%m%Y')
        ET.SubElement(declarbody, 'HNUM').text = self.number
        if self.number1 is not False:
            ET.SubElement(declarbody, 'HNUM1').text = self.number1
        else:
            ET.SubElement(declarbody, 'HNUM1').set('xsi:nil', 'true')
        if self.number2 is not False:
            ET.SubElement(declarbody, 'HNUM2').text = self.number2
        else:
            ET.SubElement(declarbody, 'HNUM2').set('xsi:nil', 'true')
        if self.category == 'out_tax_invoice':
            ET.SubElement(declarbody, 'HNAMESEL').text = self.company_id.name
            ET.SubElement(declarbody, 'HNAMEBUY').text = \
                self.partner_id.parent_name or self.partner_id.name
            ET.SubElement(declarbody, 'HKSEL').text = self.company_id.vat
            ET.SubElement(declarbody, 'HKBUY').text = self.ipn_partner
            comp_adr = ''
            if self.company_id.zip:
                comp_adr += self.company_id.zip
            if self.company_id.state_id:
                if self.company_id.state_id.name:
                    comp_adr += ', ' + self.company_id.state_id.name
            if self.company_id.city:
                comp_adr += ', ' + self.company_id.city
            if self.company_id.street:
                comp_adr += ', ' + self.company_id.street
            if self.company_id.street2:
                comp_adr += ', ' + self.company_id.street2
            ET.SubElement(declarbody, 'HLOCSEL').text = comp_adr
            ET.SubElement(declarbody, 'HLOCBUY').text = self.adr_partner
            ET.SubElement(declarbody, 'HTELSEL').text = self.company_id.phone
            ET.SubElement(declarbody, 'HTELBUY').text = self.tel_partner
        else:   # in tax invoice
            ET.SubElement(declarbody, 'HNAMEBUY').text = self.company_id.name
            ET.SubElement(declarbody, 'HNAMESEL').text = \
                self.partner_id.parent_name or self.partner_id.name
            ET.SubElement(declarbody, 'HKBUY').text = self.company_id.vat
            ET.SubElement(declarbody, 'HKSEL').text = self.ipn_partner
            comp_adr = ''
            if self.company_id.zip:
                comp_adr += self.company_id.zip
            if self.company_id.state_id:
                if self.company_id.state_id.name:
                    comp_adr += ', ' + self.company_id.state_id.name
            if self.company_id.city:
                comp_adr += ', ' + self.company_id.city
            if self.company_id.street:
                comp_adr += ', ' + self.company_id.street
            if self.company_id.street2:
                comp_adr += ', ' + self.company_id.street2
            ET.SubElement(declarbody, 'HLOCBUY').text = comp_adr
            ET.SubElement(declarbody, 'HLOCSEL').text = self.adr_partner
            ET.SubElement(declarbody, 'HTELBUY').text = self.company_id.phone
            ET.SubElement(declarbody, 'HTELSEL').text = self.tel_partner

        if self.contract_type:
            ET.SubElement(declarbody, 'H01G1S').text = \
                self.contract_type.name
        else:
            ET.SubElement(declarbody, 'H01G1S').set('xsi:nil', 'true')
        if self.contract_date is not False:
            contr_date = fields.Date.from_string(self.contract_date)
            ET.SubElement(declarbody, 'H01G2D').text = \
                contr_date.strftime('%d%m%Y')
        else:
            ET.SubElement(declarbody, 'H01G2D').set('xsi:nil', 'true')
        if self.contract_numb is not False:
            ET.SubElement(declarbody, 'H01G3S').text = self.contract_numb
        else:
            ET.SubElement(declarbody, 'H01G3S').set('xsi:nil', 'true')
        if self.payment_meth:
            ET.SubElement(declarbody, 'H02G1S').text = self.payment_meth.name
        else:
            ET.SubElement(declarbody, 'H02G1S').set('xsi:nil', 'true')
        # for tax lines loop
        row_num = 0
        for tl in self.taxinvoice_line_ids:
            row_num += 1
            tl_date = fields.Date.from_string(tl.date_vynyk)
            el = ET.SubElement(declarbody, 'RXXXXG2D')
            el.text = tl_date.strftime('%d%m%Y')
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG3S')
            el.text = tl.product_id.name
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG4')
            if tl.ukt_zed:
                el.text = tl.ukt_zed
            else:
                el.set('xsi:nil', 'true')
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG4S')
            el.text = tl.uom_id.name
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG105_2S')
            if tl.uom_id.uom_code:
                el.text = tl.uom_id.uom_code
            else:
                el.set('xsi:nil', 'true')
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG5')
            el.text = str(tl.quantity)
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG6')
            el.text = str(tl.price_unit)
            el.set('ROWNUM', str(row_num))

            tax_id = tl.taxinvoice_line_tax_id
            el = ET.SubElement(declarbody, 'RXXXXG7')
            if tax_id.name.find(u"ПДВ 20%") >= 0:
                el.text = str(tl.price_subtotal)
            else:
                el.set('xsi:nil', 'true')
            el.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG109')
            if tax_id.name.find(u"ПДВ 7%") >= 0:
                el.text = str(tl.price_subtotal)
            else:
                el.set('xsi:nil', 'true')
            el.set('ROWNUM', str(row_num))

            el8 = ET.SubElement(declarbody, 'RXXXXG8')
            el9 = ET.SubElement(declarbody, 'RXXXXG9')
            if tax_id.name.find(u"ПДВ 0%") >= 0:
                if self.htypr == '07':  # if export
                    el9.text = str(tl.price_subtotal)
                    el8.set('xsi:nil', 'true')
                else:
                    el8.text = str(tl.price_subtotal)
                    el9.set('xsi:nil', 'true')
            else:
                el8.set('xsi:nil', 'true')
                el9.set('xsi:nil', 'true')
            el8.set('ROWNUM', str(row_num))
            el9.set('ROWNUM', str(row_num))

            el = ET.SubElement(declarbody, 'RXXXXG10')
            if tax_id.name.find(u"від ПДВ") >= 0:
                el.text = str(tl.price_subtotal)
            else:
                el.set('xsi:nil', 'true')
            el.set('ROWNUM', str(row_num))
        # subtotal
        found_20 = found_7 = found_0 = found_zv = False
        for tx in self.tax_line_ids:
            if tx.name.find(u"ПДВ 20%") >= 0 and not found_20:
                found_20 = True
                ET.SubElement(declarbody, 'R01G7').text = str(tx.base)
                ET.SubElement(declarbody, 'R03G7').text = str(tx.amount)
                ET.SubElement(declarbody, 'R04G7').text = \
                    str(tx.base + tx.amount)
                continue
            if tx.name.find(u"ПДВ 7%") >= 0 and not found_7:
                found_7 = True
                ET.SubElement(declarbody, 'R01G109').text = str(tx.base)
                ET.SubElement(declarbody, 'R03G109').text = str(tx.amount)
                ET.SubElement(declarbody, 'R04G109').text = \
                    str(tx.base + tx.amount)
                continue
            if tx.name.find(u"ПДВ 0%") >= 0 and not found_0:
                found_0 = True
                if self.htypr == '07':  # if export
                    ET.SubElement(declarbody, 'R01G9').text = str(tx.base)
                    ET.SubElement(declarbody, 'R04G9').text = str(tx.base)
                    ET.SubElement(declarbody, 'R01G8').set('xsi:nil', 'true')
                    ET.SubElement(declarbody, 'R04G8').set('xsi:nil', 'true')
                else:
                    ET.SubElement(declarbody, 'R01G8').text = str(tx.base)
                    ET.SubElement(declarbody, 'R04G8').text = str(tx.base)
                    ET.SubElement(declarbody, 'R01G9').set('xsi:nil', 'true')
                    ET.SubElement(declarbody, 'R04G9').set('xsi:nil', 'true')
                continue
            if tx.name.find(u"від ПДВ") >= 0 and not found_zv:
                found_zv = True
                ET.SubElement(declarbody, 'R01G10').text = str(tx.base)
                ET.SubElement(declarbody, 'R04G10').text = str(tx.base)
                ET.SubElement(declarbody, 'R03G10S').text = u"Звільнено"
                continue
        if not found_20:
            ET.SubElement(declarbody, 'R01G7').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R03G7').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R04G7').set('xsi:nil', 'true')
        if not found_7:
            ET.SubElement(declarbody, 'R01G109').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R03G109').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R04G109').set('xsi:nil', 'true')
        if not found_0:
            ET.SubElement(declarbody, 'R01G8').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R04G8').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R01G9').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R04G9').set('xsi:nil', 'true')
        if not found_zv:
            ET.SubElement(declarbody, 'R01G10').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R04G10').set('xsi:nil', 'true')
            ET.SubElement(declarbody, 'R03G10S').set('xsi:nil', 'true')
        # total
        if self.amount_untaxed:
            ET.SubElement(declarbody, 'R01G11').text = str(self.amount_untaxed)
        else:
            ET.SubElement(declarbody, 'R01G11').set('xsi:nil', 'true')
        if self.amount_tara > 0:
            ET.SubElement(declarbody, 'R02G11').text = str(self.amount_tara)
        else:
            ET.SubElement(declarbody, 'R02G11').set('xsi:nil', 'true')
        if self.amount_tax:
            ET.SubElement(declarbody, 'R03G11').text = str(self.amount_tax)
        else:
            ET.SubElement(declarbody, 'R03G11').set('xsi:nil', 'true')
        if self.amount_total:
            ET.SubElement(declarbody, 'R04G11').text = str(self.amount_total)
        else:
            ET.SubElement(declarbody, 'R04G11').set('xsi:nil', 'true')
        # footer
        ET.SubElement(declarbody, 'H10G1S').text = self.signer_id.name
        ET.SubElement(declarbody, 'R003G10S').text = self.prych_zv

        xmldata = ET.tostring(declar,
                              encoding='windows-1251',
                              method='xml')
        return xmldata, fname


class TaxInvoiceLine(models.Model):
    _name = 'account.taxinvoice.line'
    _description = 'Tax Invoice Line'

    @api.one
    @api.depends('price_unit', 'discount', 'taxinvoice_line_tax_id',
                 'quantity', 'product_id')
    def _compute_subtotal(self):
        if self.taxinvoice_id:
            currency = self.taxinvoice_id.currency_id
        if not currency:
            currency = self.company_id.currency_id

        tl_id = self.taxinvoice_line_tax_id
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        self.price_subtotal = self.quantity * price
        self.tax_amount = self.price_subtotal * tl_id.amount / 100
        if currency:
            self.price_subtotal = currency.round(self.price_subtotal)
            self.tax_amount = currency.round(self.tax_amount)

    sequence = fields.Integer(string=u"Послідовність", default=10,
                              help=u"Перетягніть для зміни порядкового номеру")
    taxinvoice_id = fields.Many2one('account.taxinvoice',
                                    string=u"Посилання на ПН",
                                    ondelete='cascade', index=True)
    date_vynyk = fields.Date(string=u"Дата виникнення ПЗ", index=True,
                             help=u"Дата першої події з ПДВ",
                             copy=True, required=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='restrict',
                                 index=True, required=True)
    uom_id = fields.Many2one('product.uom', string=u"Одиниця виміру",
                             ondelete='set null', index=True, required=True)
    uom_code = fields.Char(string=u"Код одиниць",
                           help=u"Код одниниць виміру згідно КСПОВО",
                           size=4)
    price_unit = fields.Float(string=u"Ціна за одиницю",
                              digits=dp.get_precision('Product Price'),
                              default=0, required=True)
    discount = fields.Float(string=u"Скидка (%)",
                            digits=dp.get_precision('Discount'),
                            default=0.0)
    quantity = fields.Float(string=u"Кількість",
                            digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)
    ukt_zed = fields.Char(string=u"Код УКТ ЗЕД",
                          help=u"Код згідно УКТ ЗЕД",
                          size=10)
    taxinvoice_line_tax_id = fields.Many2one('account.tax',
                                             string=u"Ставка податку",
                                             required=True,
                                             domain="[('type_tax_use', 'in', \
                                                      {'out_tax_invoice': \
                                                       ['sale'], \
                                                       'in_tax_invoice': \
                                                       ['purchase']}.get( \
                                                       parent.category, [])), \
                                                       ('company_id', '=', \
                                                       parent.company_id), \
                                                       ('name', 'like', \
                                                       u'ПДВ')]")
    price_subtotal = fields.Float(string=u"Сума",
                                  digits=dp.get_precision('Account'),
                                  store=True,
                                  readonly=True,
                                  compute='_compute_subtotal'
                                  )
    account_id = fields.Many2one('account.account', string=u"Рахунок",
                                 domain=[('deprecated', '=', False)],
                                 help=u"Рахунок підтверженного ПДВ")
    tax_amount = fields.Float(string=u"Сума податку",
                              digits=dp.get_precision('Account'),
                              store=True,
                              compute='_compute_subtotal')

    @api.onchange('product_id')
    def onchange_product_id(self):
        """Update other fields when product is changed."""
        domain = {}
        if not self.taxinvoice_id:
            return

        if not self.taxinvoice_id.partner_id:
            warning = {
                'title': _(u"Попередження!"),
                'message': _(u"Спочатку оберіть партнера!"),
            }
            return {'warning': warning}

        company = self.taxinvoice_id.company_id
        currency = self.taxinvoice_id.currency_id
        category = self.taxinvoice_id.category

        if not self.product_id:
            self.date_vynyk = self.taxinvoice_id.date_vyp
            self.price_unit = 0.0
            self.quantity = 1
            self.ukt_zed = ''
            if self.uom_id:
                if self.uom_code != self.uom_id.uom_code:
                    self.uom_code = self.uom_id.uom_code
            else:
                self.uom_code = ''
            if self.taxinvoice_line_tax_id:
                if self.account_id != self.taxinvoice_line_tax_id.account_id:
                    self.account_id = self.taxinvoice_line_tax_id.account_id

            domain['uom_id'] = []
        else:
            product = self.product_id
            self.ukt_zed = product.ukt_zed

            if category == 'out_tax_invoice':
                taxes = product.taxes_id
            else:
                taxes = product.supplier_taxes_id

            if taxes:
                found = False
                for t in taxes:
                    if not found:
                        if t.company_id == company:
                            if t.name.find(u"ПДВ") >= 0:
                                self.taxinvoice_line_tax_id = t
                                found = True
                    else:
                        break
            else:
                self.taxinvoice_line_tax_id = None

            if self.taxinvoice_line_tax_id:
                if self.taxinvoice_line_tax_id.account_id:
                    self.account_id = self.taxinvoice_line_tax_id.account_id
                else:
                    self.account_id = None
            else:
                self.account_id = None

            if category == 'in_tax_invoice':
                self.price_unit = self.price_unit or \
                    product.standard_price
            else:
                self.price_unit = product.lst_price

            if not self.uom_id or \
                    product.uom_id.category_id.id != \
                    self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
                self.uom_code = product.uom_id.uom_code
            if self.uom_id:
                if self.uom_code != self.uom_id.uom_code:
                    self.uom_code = self.uom_id.uom_code

            if company and currency:
                if company.currency_id != currency:
                    if category == 'in_tax_invoice':
                        self.price_unit = product.standard_price
                    self.price_unit = self.price_unit * \
                        currency.with_context(dict(self._context or {},
                                                   date=self.date_vynyk)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = \
                        self.env['product.uom']._compute_price(
                            product.uom_id.id, self.price_unit, self.uom_id.id)

            domain['uom_id'] = [
                ('category_id', '=', product.uom_id.category_id.id)]

        return {'domain': domain}

    @api.onchange('uom_id')
    def onchange_uom_id(self):
        """Update uom_code field when uom_id is changed."""
        warning = {}
        result = {}
        self.onchange_product_id()
        if not self.uom_id:
            self.price_unit = 0.0
        if self.product_id and self.uom_id:
            if self.product_id.uom_id.category_id.id != \
               self.uom_id.category_id.id:
                warning = {
                    'title': _(u"Попередження!"),
                    'message': _("Обрана одиниця виміру не "
                                 "сумісна з одиницею виміру "
                                 "товару."),
                }
                self.uom_id = self.product_id.uom_id.id
        if warning:
            result['warning'] = warning
        return result

    @api.onchange('taxinvoice_line_tax_id')
    def onchange_taxinvoice_line_tax_id(self):
        """Update account_id field when taxinvoice_line_tax_id is changed."""
        if self.taxinvoice_line_tax_id:
            if self.taxinvoice_line_tax_id.account_id:
                self.account_id = self.taxinvoice_line_tax_id.account_id
            else:
                self.account_id = None
        else:
            self.account_id = None


class TaxInvoiceTax(models.Model):
    _name = 'account.taxinvoice.tax'
    _description = 'Tax Invoice taxes'
    _order = 'sequence'

    sequence = fields.Integer(string=u"Послідовність",
                              help=u"Перетягніть для зміни порядкового номеру")
    taxinvoice_id = fields.Many2one('account.taxinvoice',
                                    string=u"Посилання на ПН",
                                    ondelete='cascade', index=True)
    name = fields.Char(string=u"Назва податку",
                       required=True)
    account_id = fields.Many2one('account.account', string=u"Рахунок податку",
                                 required=True)
    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string=u"Аналітичний рахунок")
    base = fields.Monetary(string=u"База", readonly=True)
    amount = fields.Monetary(string=u"Сума")
    manual = fields.Boolean(string=u"Вручну", default=True)
    company_id = fields.Many2one('res.company',
                                 string=u"Компанія",
                                 related='account_id.company_id',
                                 store=True, readonly=True)
    tax_id = fields.Many2one('account.tax', string=u"Податок")
    currency_id = fields.Many2one('res.currency',
                                  related='taxinvoice_id.currency_id',
                                  store=True, readonly=True)
