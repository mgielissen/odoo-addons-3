# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
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
                             ('draft', 'Draft'),
                             ('proforma', 'Pro-forma'),   # TODO edit states
                             ('proforma2', 'Pro-forma'),
                             ('open', 'Open'),
                             ('paid', 'Paid'),
                             ('cancel', 'Cancelled'),
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

    h01 = fields.Boolean(string=u"Складається інвестором", default=False)
    horig1 = fields.Boolean(string=u"Не видається покупцю", default=False)
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
        track_visibility='always')

    date_vyp = fields.Date(string=u"Дата документу", index=True,
                           readonly=True,
                           states={'draft': [('readonly', False)]},
                           help=u"Дата першої події з ПДВ",
                           copy=True,
                           required=True)

    date_reg = fields.Date(string=u"Дата реєстрації", index=True,
                           readonly=True,
                           states={'draft': [('readonly', False)]},
                           help=u"Дата реєстрації в ЄРПН",
                           copy=False)

    # TODO change to char
    number = fields.Integer(string=u"Номер ПН", size=7)
    number1 = fields.Integer(string=u"Ознака спеціальної ПН", size=1)
    number2 = fields.Integer(string=u"Код філії", size=4)

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
        change_default=True, default='pn',
        track_visibility='always')

    company_seller = fields.Many2one('res.partner',
                                     string=u"Продавець", ondelete='set null',
                                     help=u"Компанія-постачальник", index=True)

    company_buyer = fields.Many2one('res.partner',
                                    string=u"Покупець", ondelete='set null',
                                    help=u"Компанія-отримувач", index=True)

    ipn_seller = fields.Char(string=u"ІПН продавця")
    ipn_buyer = fields.Char(string=u"ІПН покупця")
    adr_seller = fields.Char(string=u"Адреса продавця")
    adr_buyer = fields.Char(string=u"Адреса покупця")
    tel_seller = fields.Char(string=u"Телефон продавця")
    tel_buyer = fields.Char(string=u"Телефон покупця")

    contract_type = fields.Many2one('account.taxinvoice.contrtype',
                                    string=u"Тип договору",
                                    ondelete='set null',
                                    help=u"Тип договору згідно ЦКУ",
                                    index=True)
    contract_date = fields.Date(string=u"Дата договору")
    contract_numb = fields.Char(string=u"Номер договору")
    payment_meth = fields.Many2one('account.taxinvoice.paymeth',
                                   string=u"Спосіб оплати",
                                   ondelete='set null',
                                   help=u"Спосіб оплати за постачання",
                                   index=True)

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

    @api.onchange('company_seller')
    def update_seller_info(self):
        if not self.company_seller:
            return
        else:
            self.ipn_seller = self.company_seller.vat if \
                self.company_seller.vat else ''
            self.tel_seller = self.company_seller.phone if \
                self.company_seller.phone else ''
            self.adr_seller = ''
            if self.company_seller.zip:
                self.adr_seller = self.adr_seller + self.company_seller.zip
            if self.company_seller.state_id.name:
                self.adr_seller = self.adr_seller + ', ' + \
                    self.company_seller.state_id.name
            if self.company_seller.city:
                self.adr_seller = self.adr_seller + \
                    ', ' + self.company_seller.city
            if self.company_seller.street:
                self.adr_seller = self.adr_seller + \
                    ', ' + self.company_seller.street
            if self.company_seller.street2:
                self.adr_seller = self.adr_seller + \
                    ', ' + self.company_seller.street2
        return {}

    @api.onchange('company_buyer')
    def update_buyer_info(self):
        if not self.company_buyer:
            return
        else:
            self.ipn_buyer = self.company_buyer.vat if \
                self.company_buyer.vat else ''
            self.tel_buyer = self.company_buyer.phone if \
                self.company_buyer.phone else ''
            self.adr_buyer = ''
            if self.company_buyer.zip:
                self.adr_buyer = self.adr_buyer + self.company_buyer.zip
            if self.company_buyer.state_id.name:
                self.adr_buyer = self.adr_buyer + ', ' + \
                    self.company_buyer.state_id.name
            if self.company_buyer.city:
                self.adr_buyer = self.adr_buyer + \
                    ', ' + self.company_buyer.city
            if self.company_buyer.street:
                self.adr_buyer = self.adr_buyer + \
                    ', ' + self.company_buyer.street
            if self.company_buyer.street2:
                self.adr_buyer = self.adr_buyer + \
                    ', ' + self.company_buyer.street2
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
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency_id or journal.company_id.currency_id

    taxinvoice_line = fields.One2many('account.taxinvoice.line',
                                      'taxinvoice_id',
                                      string=u"Рядки ПН",
                                      readonly=True,
                                      states={'draft': [('readonly', False)]},
                                      copy=True)
    tax_line = fields.One2many('account.taxinvoice.tax', 'taxinvoice_id',
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
                                 domain="[('company_id', '=', company_id)]"
                                 )
    company_id = fields.Many2one('res.company',
                                 string=u"Компанія",
                                 change_default=True,
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: (
                                  self.env['res.company']._company_default_get(
                                     'account.invoice')))
    account_id = fields.Many2one('account.account',
                                 string=u"Рахунок",
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 domain=[('deprecated', '=', False)],
                                 help=u"Рахунок розрахунків по ПДВ")
    fiscal_position_id = fields.Many2one('account.fiscal.position',  # Drop me
                                         string='Fiscal Position',
                                         oldname='fiscal_position',
                                         readonly=True,
                                         states={'draft': [('readonly',
                                                            False)]})


class TaxInvoiceLine(models.Model):
    _name = 'account.taxinvoice.line'
    _description = 'Tax Invoice Line'

    @api.one
    @api.depends('price_unit', 'discount', 'taxinvoice_line_tax_id',
                 'quantity', 'product_id')
    def _compute_subtotal(self):
        if self.taxinvoice_id:
            currency = self.taxinvoice_id.currency_id
            if self.taxinvoice_id.category == 'out_tax_invoice':
                partner = self.taxinvoice_id.company_buyer
            if self.taxinvoice_id.category == 'in_tax_invoice':
                partner = self.taxinvoice_id.company_seller
        else:
            currency = None
            partner = None

        tl_id = self.taxinvoice_line_tax_id
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = tl_id.compute_all(price,
                                  currency,
                                  self.quantity,
                                  product=self.product_id,
                                  partner=partner)
        if taxes:
            self.price_subtotal = price_subtotal_sign = taxes['total_excluded']
        else:
            self.price_subtotal = price_subtotal_sign = self.quantity * price

        # if currency:
        #     if currency != self.taxinvoice_id.company_id.currency_id:
        #         price_subtotal_sign = \
        #             currency.compute(price_subtotal_sign,
        #                             self.taxinvoice_id.company_id.currency_id)
        # sign= self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        # self.price_subtotal_signed = price_subtotal_signed * sign
        # used to calculate signed subtotal for analytic line

    sequence = fields.Integer(string=u"Послідовність", default=10,
                              help=u"Перетягніть для зміни порядкового номеру")
    taxinvoice_id = fields.Many2one('account.taxinvoice',
                                    string=u"Посилання на ПН",
                                    ondelete='cascade', index=True)
    date_vynyk = fields.Date(string=u"Дата виникнення ПЗ", index=True,
                             help=u"Дата першої події з ПДВ",
                             copy=True, required=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='restrict', index=True)
    uom_id = fields.Many2one('product.uom', string=u"Одиниця виміру",
                             ondelete='set null', index=True)
    uom_code = fields.Char(string=u"Код КСПОВО",
                           help=u"Код одниниць згідно КСПОВО",
                           size=4)
    price_unit = fields.Float(string=u"Ціна за одиницю", required=True,
                              digits=dp.get_precision('Product Price'),
                              default=0)
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
                                             )
    price_subtotal = fields.Float(string=u"Вартість",
                                  digits=dp.get_precision('Account'),
                                  store=True,
                                  readonly=True,
                                  compute='_compute_subtotal'
                                  )
    account_id = fields.Many2one('account.account', string=u"Рахунок",
                                 required=True,
                                 domain=[('deprecated', '=', False)],
                                 help=u"Рахунок підтверженного ПДВ")

    @api.onchange('product_id')
    def onchange_product_id(self):
        """Update other fields when product is changed."""
        domain = {}
        if not self.taxinvoice_id:
            return

        company = self.taxinvoice_id.company_id
        currency = self.taxinvoice_id.currency_id
        category = self.taxinvoice_id.category

        if not self.product_id:
            self.price_unit = 0.0
            self.quantity = 0.0
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
                            if t.name.find(u"ПДВ"):
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
        self.onchange_product_id()


class TaxInvoiceTax(models.Model):
    _name = 'account.taxinvoice.tax'
    _description = 'Tax Invoice taxes'
    _order = 'sequence'

    sequence = fields.Integer(string=u"Послідовність", default=10,
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
    amount = fields.Monetary()
    manual = fields.Boolean(string=u"Вручну", default=True)
    company_id = fields.Many2one('res.company',
                                 string=u"Компанія",
                                 related='account_id.company_id',
                                 store=True, readonly=True)
    tax_id = fields.Many2one('account.tax', string=u"Податок")
    currency_id = fields.Many2one('res.currency',
                                  related='taxinvoice_id.currency_id',
                                  store=True, readonly=True)
