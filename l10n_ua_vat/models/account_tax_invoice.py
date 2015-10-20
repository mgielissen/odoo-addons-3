# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


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
                             string='Status',
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
        company_id = self._context.get('company_id',
                                       self.env.user.company_id.id)
        domain = [('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)
        # TODO fix domains here. see account.invoice

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
    # company_currency_id = fields.Many2one('res.currency',
    #                                       related='company_id.currency_id',
    #                                       readonly=True)
    # no conpany_id here!
    journal_id = fields.Many2one('account.journal',
                                 string='Journal',
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=_default_journal,
                                 domain="[('category', 'in', \
                                          {'out_tax_invoice': ['sale'], \
                                           'in_tax_invoice': ['purchase'], \
                                           }.get(type, [])), ]")
    # TODO fix domain here


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
                company = self.taxinvoice_id.company_seller
            if self.taxinvoice_id.category == 'in_tax_invoice':
                partner = self.taxinvoice_id.company_seller
                company = self.taxinvoice_id.company_buyer
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
            self.price_subtotal = taxes['total_excluded']
        else:
            self.price_subtotal = self.quantity * price

        if currency:
            if currency != company.currency_id:
                price_subtotal_signed = \
                    currency.compute(price_subtotal_signed,
                                     company.currency_id)

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
    taxinvoice_line_tax_id = fields.Many2many('account.tax',
                                              'account_invoice_line_tax',
                                              'invoice_line_id', 'tax_id',
                                              string=u"Ставка податку")
    price_subtotal = fields.Float(string=u"Вартість",
                                  digits=dp.get_precision('Account'),
                                  store=True,
                                  readonly=True,
                                  compute='_compute_subtotal'
                                  )

    @api.onchange('product_id')
    def onchange_product_id(self):
        """Update other fields when product is changed."""
        # TODO UPDATE onchange_product_id function with new fields
        domain = {}
        if not self.taxinvoice_id:
            return

        if not self.product_id:
            self.price_unit = 0.0
            self.quantity = 0.0
            self.ukt_zed = ''
            self.uom_code = ''
            domain['uom_id'] = []
        else:
            self.ukt_zed = self.product_id.ukt_zed

            if not self.uom_id or \
                    self.product_id.uom_id.category_id.id != \
                    self.uom_id.category_id.id:
                self.uom_id = self.product_id.uom_id.id
                self.uom_code = self.product_id.uom_id.uom_code

            domain['uom_id'] = [
                ('category_id', '=', self.product_id.uom_id.category_id.id)]

        return {'domain': domain}


class TaxInvoiceTax(models.Model):
    _name = 'account.taxinvoice.tax'
    _description = 'Tax Invoice taxes'

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
    base = fields.Float(string=u"База", digits=dp.get_precision('Account'))
    amount = fields.Float(string=u"Величина",
                          digits=dp.get_precision('Account'))
    manual = fields.Boolean(string=u"Вручну", default=True)
    base_code_id = fields.Many2one('account.tax.code', string=u"Код бази",
                                   help=u"Код бази оподаткування")
    base_amount = fields.Float(string=u"Величина бази податку",
                               digits=dp.get_precision('Account'),
                               default=0.0)
    tax_code_id = fields.Many2one('account.tax.code', string=u"Код податку",
                                  help=u"Код величини податку")
    tax_amount = fields.Float(string=u"Величина податку",
                              digits=dp.get_precision('Account'),
                              default=0.0)
