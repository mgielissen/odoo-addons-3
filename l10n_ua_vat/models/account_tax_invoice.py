# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class TIContrType(models.Model):
    _name = 'account.taxinvoice.contrtype'
    _description = 'Tax Invoice Contract Type'

    name = fields.Char(string='Typ dogovoru')


class TIPayMeth(models.Model):
    _name = 'account.taxinvoice.paymeth'
    _description = 'Tax Invoice Payment method'

    name = fields.Char(string='Sposib oplaty')


class TaxInvoice(models.Model):
    _name = 'account.taxinvoice'
    _description = 'Tax Invoice'

    h01 = fields.Boolean(string='Skladaetsya investorom', default=False)
    horig1 = fields.Boolean(string='Ne vydaetsya pokuptsyu', default=False)
    htypr = fields.Selection([
        ('00', 'Nemae'),
        ('01', '01 - '
         'Vypysana na sumu perevyshchennya zvychaynoyi tsiny nad faktychnoyu'),
        ('02', '02 - '
         'Postachannya neplatnyku podatku'),
        ('03', '03 - '
         'Naturalna vyplata v rakhunok oplaty pratsi fizychnym osobam'),
        ('04', '04 - '
         'Postachannya u mezhakh balansu dlya nevyrobnychoho vykorystann'),
        ('05', '05 - '
         'Likvidatsiya osnovnykh zasobiv za rishennyam platnyka podatku'),
        ('06', '06 - '
         'Perevedennya vyrobnychykh osnovnykh zasobiv do nevyrobnychykh'),
        ('07', '07 - '
         'Eksportni postachannya'),
        ('08',
         '08 - '
         'Postachannya dlya operatsiy, yaki ne ye obyektom opodatkuvannya'),
        ('09',
         '09 - '
         'Postachannya dlya operatsiy, yaki zvilneni vid opodatkuvannya'),
        ('10', '10 - '
         'Vyznannya umovnoho postachannya tovarnykh zalyshkiv'),
        ('11', '11 - '
         'Vypysana za shchodennymy pidsumkamy operatsiy'),
        ('12',
         '12 - '
         'Vypysana na vartist bezoplatno postavlenykh tovariv-posluh'),
        ('13',
         '13 - '
         'Vykorystannya zasobiv, tovariv-posluh ne u hospodarskiy diyalnosti'),
        ('14',
         '14 - '
         'Vypysana pokuptsem (otrymuvachem) posluh vid nerezydenta'),
        ('15', '15 - '
         'Skladena na sumu perevyshchennya tsiny prydbannya'),
        ('16',
         '16 - '
         'Skladena na sumu perevyshchennya balansovoyi vartosti'),
        ('17',
         '17 - '
         'Skladena na sumu perevyshchennya sobivartosti vyhotovlenyh tovariv'),
    ], string='Typ prychyny', index=True,
        change_default=True, default='00',
        track_visibility='always')

    date_vyp = fields.Date(string='Data dokumentu', index=True,
                           # TODO readonly=True, states={'draft': [('readonly',
                           # False)]},
                           help="Data pershoi podii z PDV", copy=True,
                           required=True)

    date_reg = fields.Date(string='Data reestracii', index=True,
                           # TODO readonly=True, states={'draft': [('readonly',
                           # False)]},
                           help="Data reestracii dokumentu v ERPN", copy=False)

    # TODO change to char
    number = fields.Integer(string='Nomer PN', size=7)
    number1 = fields.Integer(string='Oznaka specialnoi PN', size=1)
    number2 = fields.Integer(string='Kod Filii', size=4)

    category = fields.Selection([
        ('out_tax_invoice', 'Vydani PN'),
        ('in_tax_invoice', 'Otrymani PN'),
    ], string='Category', readonly=True,
        index=True, change_default=True,
        default=lambda self: self._context.get('category', 'out_tax_invoice'),
        track_visibility='always')

    doc_type = fields.Selection([
        ('pn', 'Podatkova nakladna'),
        ('rk', 'Rozrakhunok koryguvannya do PN'),
        ('vmd', 'Mytna deklaratsiya'),
        ('tk', 'Transportnyj kvytok'),
        ('bo', 'Buhgalterska dovidka'),
    ], string='Typ dokumentu', index=True,
        change_default=True, default='pn',
        track_visibility='always')

    company_seller = fields.Many2one('res.partner',
                                     string="Prodavets", ondelete='set null',
                                     help='Kompaniya postachalnyk', index=True)

    company_buyer = fields.Many2one('res.partner',
                                    string="Pokupets", ondelete='set null',
                                    help='Kompaniya pokupets', index=True)

    ipn_seller = fields.Char(string='IPN prodavtsya')
    ipn_buyer = fields.Char(string='IPN pokuptsya')
    adr_seller = fields.Char(string='Adresa prodavtsya')
    adr_buyer = fields.Char(string='Adresa pokuptsya')
    tel_seller = fields.Char(string='Telefon prodavtsya')
    tel_buyer = fields.Char(string='Telefon pokuptsya')

    contract_type = fields.Many2one('account.taxinvoice.contrtype',
                                    string="Typ dogovoru", ondelete='set null',
                                    help='Typ dogovoru zgidno civiln kodeksu',
                                    index=True)
    contract_date = fields.Date(string='Data dogovoru')
    contract_numb = fields.Char(string='Nomer dogovoru')
    payment_meth = fields.Many2one('account.taxinvoice.paymeth',
                                   string="Sposib oplaty", ondelete='set null',
                                   help='Sposib oplatu za postachannya',
                                   index=True)

    # Modified record name on form view
    @api.multi
    def name_get(self):
        TYPES = {
            'pn': 'Podatkova nakladna',
            'rk': 'Rozrakhunok koryguvannya do PN',
            'vmd': 'Mytna deklaratsiya',
            'tk': 'Transportnyj kvytok',
            'bo': 'Buhgalterska dovidka',
        }
        result = []
        for inv in self:
            date = fields.Date.from_string(inv.date_vyp)
            datef = date.strftime('%d.%m.%Y')
            result.append(
                (inv.id, "%s # %s vid %s" % (TYPES[inv.doc_type], inv.number,
                                             datef)))
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

    taxinvoice_line = fields.One2many('account.taxinvoice.line',
                                      'taxinvoice_id',
                                      string=' Tax Invoice Lines',
                                      # TODO readonly=True, states={'draft':
                                      # [('readonly', False)]},
                                      copy=True)


class TaxInvoiceLine(models.Model):
    _name = 'account.taxinvoice.line'
    _description = 'Tax Invoice Line'

    sequence = fields.Integer(string='Sequence', default=10,
                              help="Gives the sequence of this line "
                                   "when displaying the tax invoice.")
    taxinvoice_id = fields.Many2one('account.taxinvoice',
                                    string=' Tax Invoice Reference',
                                    ondelete='cascade', index=True)
    date_vynyk = fields.Date(string='Data vynyknennya PZ', index=True,
                             help="Data pershoi podii z PDV",
                             copy=True, required=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='restrict', index=True)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure',
                             ondelete='set null', index=True)
    price_unit = fields.Float(string='Unit Price', required=True,
                              digits=dp.get_precision('Product Price'),
                              default=0)
    quantity = fields.Float(string='Quantity',
                            digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)
    ukt_zed = fields.Char(string='Kod UKT ZED',
                          help="Kod zgidno UKT ZED",
                          size=10)

    # TODO add @api.onchange for product field
    # to update uom and oum_code
    #
    # add uom_code field

    @api.onchange('product_id')
    def update_ukt_zed(self):
        self.ukt_zed = self.product_id.ukt_zed
        return {}
