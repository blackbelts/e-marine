from datetime import timedelta, datetime
import xlsxwriter
from xlsxwriter.workbook import Workbook
import base64
import xlrd
from xlrd import open_workbook
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models
class PolicyMarine(models.Model):
      _name='policy.marine'
      _rec_name = 'cover_num'

      # customer=fields.Many2one('res.partner',string='Customer')
      @api.model
      def create(self, vals):
            if vals.get('is_endorsement')==True:
                  return super(PolicyMarine, self).create(vals)
            else:
                  serial_no = self.env['ir.sequence'].next_by_code('policy')
                  type=vals.get('marine_type')
                  currency=vals.get('currency_id')
                  cur = self.env['res.currency'].search([('id','=',currency)]).name
                  marine_type = self.env['insurance.product'].search([('id','=',type)]).product_name

                  vals['cover_num'] = str(marine_type).upper() +'/'+str(cur)+ str(serial_no)
                  return super(PolicyMarine, self).create(vals)

      cover_num=fields.Char('Open Cover',readonly=True)
      insured=fields.Char('Insured')
      lob = fields.Many2one('insurance.line.business', 'LOB',required=True,domain="[('line_of_business','in',['Cargo','Inland'])]")
      marine_type = fields.Many2one('insurance.product', 'Code',required=True,domain="[('line_of_bus','=',lob)]")

      in_favour=fields.Char('IN Favour of')
      address=fields.Char(' Insured Address')
      issue_date=fields.Date('Issuance Date',default=datetime.today())
      start_date=fields.Date('Effective from',default=datetime.today())
      end_date=fields.Date('Effective To',default=datetime.today())
      active = fields.Boolean(string="Active", default=True)
      min_premium=fields.Float('Limit Net Premium')
      net_premium=fields.Float('Net Premium')
      nature_pakage=fields.Many2many('marine.package',string='Nature of pakage')
      inv_num=fields.Char('Order or Invoice No')
      ship_num=fields.Char('Bill of Leading')
      file_num=fields.Char('L/C No')
      conveyance_mode=fields.Selection([('Air or Sea Shipment', 'Air or Sea Shipment'),
                                           ('Air Shipment', 'Air Shipment'),
                                           ('Sea Shipment', 'Sea Shipment'),
                                           ('Land Shipment', 'Land Shipment'),
                                           ('air', 'نقل جوى'),
                                           ('Sea ', 'نقل بحرى'),
                                           ('Land ', 'نقل داخلى'),
                                           ('land_sea ', 'نقل جوى او بحرى'),
                                        ],string='Conveyance mode')
      ship_from=fields.Char('Country origin')
      ship_to=fields.Char('Destination Country')
      bank = fields.Char('Bank')
      carrier_name = fields.Char('Carrier/Veseel Name')
      carrier_age = fields.Char('Veseel Age')
      carrier_nation = fields.Char('Veseel Nationality')
      supplier = fields.Char('Supplier')
      consignee = fields.Char('Consignee')
      consignee_value = fields.Char('Consignee Value')
      invoice_currency = fields.Many2one('res.currency',string='Invoice Currency')
      invoice_ammount = fields.Char('Invoice Amount')
      valution_notes=fields.Many2many('marine.valuation',string='Valution Notes')
      sum_insured=fields.Float('Sum Insured')
      max_per_cert=fields.Float('Max Per Shipment')
      # terms=fields.Many2many('condition',string='Terms & Conditions' ,domain="[('type', '=', 'basic')]")
      new_terms = fields.Many2many('condition', 'term_cover_rel',  'term_id','cover_id',
                                   string='Terms & Conditions',domain="[('type', '=', 'basic')]")

      new_special_terms=fields.Many2many('condition', 'term_special_cover_rel', 'cover_special_id', 'term_special_id',
                                         string='Terms & Conditions',domain="[('type', '=', 'special')]")
      ex_terms_ids = fields.Many2many('condition', 'ex_cover_rel', 'cover_ex_id', 'ex_special_id',
                                           string='Terms & Conditions', domain="[('type', '=', 'exclusion')]")

      rate=fields.Float('Rate')
      is_endorsement = fields.Boolean(string="", default=False)
      is_canceled = fields.Boolean(string="", )
      last_cover_id = fields.Many2one('policy.marine', readonly=True)
      endorsement_type = fields.Selection([('Technical', 'Technical'),
                                           ('Non Tech', 'Non Tech'),
                                           ('canceled', 'canceled'),
                                           ('extend', 'Extend')
                                           ],
                                          string='Endorsement Type')
      cover_type = fields.Selection([('oil', 'OIL'),
                                     ('fcl', 'FCL'),
                                     ('opn', 'OPN'),
                                     ('dpn', 'DPN'),
                                     ('cil', 'CIL'),
                                     ('dil', 'DIL'),
                                     ('crg', 'CRG'),
                                     ('drg', 'DRG'),
                                     ],
                                    string='Code',required=True)
      type = fields.Selection([('individual', 'Individual'),
                               ('contract', 'Contract')],
                              default='contract',string='Policy Type', required=True)

      product=fields.Many2many('marine.product',string='Products')
      # agent_code=fields.('Agent Code')
      agent_name=fields.Many2one('res.users',  default=lambda self: self.env.user)
      agency=fields.Many2one('marine.agency',string='Shipping')
      agency_branch=fields.Many2one('agency.branch.marine',string='Shipping Branch')
      currency_id=fields.Many2one('res.currency',string='Currency',required=True)
      endorsement_no = fields.Integer(string="Endorsement Number")
      broker= fields.Many2one('res.users',string="Broker" )
      broker_person= fields.Many2one('persons',string="Broker" )
      broker_pin = fields.Char(string="Agent Code")
      broker_fra_code = fields.Char(string="Broker FRA Code" ,default=lambda self: self.broker.agent_code)
      broker_commission = fields.Float(string="Broker Commission")
      state_track = fields.Char(default='New')
      remain=fields.Float('Remaining',)
      issue_fees = fields.Float('Issue Fees')
      proportional_stamp = fields.Float('Proportional Stamp')
      dimensional_stamp = fields.Float('Dimensional Stamp')
      supervisory_stamp = fields.Float('Supervisory Stamp')
      policy_holder= fields.Float('Policy Holder Protection fund')
      revising_fees = fields.Float('Revising and approval fees')
      note = fields.Text('Notes')
      total = fields.Float('Total',compute='get_total',store=True)
      concersion_rate = fields.Float('C / Y Concersion Rate')


      @api.model
      def set_stamps(self):
          stamps={}
          if self.stamp_ids:
              for rec in self.stamp_ids:
                  stamps[rec.stamp.code]=rec.value
          return stamps

      @api.model
      def get_price(self):
          price = 0
          if self.covers_ids:
              for rec in self.covers_ids:
                  price = price + rec.rate
          return price

                  # if rec.stamp.code=='p-stamp':
                  #   self.proportional_stamp=rec.value
                  # if rec.stamp.code == 'dim-stamp':
                  #       self.dimensional_stamp = rec.value
                  # if rec.stamp.code == 's-stamp':
                  #       self.supervisory_stamp = rec.value
                  # if rec.stamp.code == 'issue-fees':
                  #       self.issue_fees = rec.value


      # @api.one
      @api.depends('stamp_ids', 'net_premium')
      def get_total(self):
            for rec in self:
                if rec.net_premium and rec.stamp_ids:
                    sum=0.0
                    for record in rec.stamp_ids:
                        sum+=record.value
                    rec.total = rec.net_premium +sum

      state = fields.Selection([('pending', 'Pending'),
                                ('approved', 'Approved'),
                                ('born-dead', 'Born-de'
                                              'ad'),
                                ('canceled', 'Canceled'), ],
                               'Status', required=True, default='pending', copy=False)

      # @api.onchange('sum_insured', 'covers_ids')
      # def set_premium(self):
      #     if self.covers_ids:
      #         for rec in self.covers_ids:
      #             if self.type == 'individual' or self.pre_paid == True:
      #                 rec.premium = (rec.rate * self.sum_insured) / 100
      #         else:
      #             rec.premium = 0.0

      @api.onchange('stamp_ids', 'net_premium')
      def set_stamp(self):
          for rec in self.stamp_ids:
              if self.type == 'individual' or self.pre_paid == True:
                  if rec.stamp.type == 'rate':
                      rec.value = (rec.stamp.rate * self.net_premium)
                  else:
                      rec.value = rec.stamp.stamp_value
              else:
                  if rec.stamp.type == 'rate':
                      rec.value = 0.0
                  else:
                      rec.value = rec.stamp.stamp_value

      @api.onchange('sum_insured','covers_ids')
      def compute_net(self):
            if self.covers_ids :
                sum = 0.0
                for rec in self.covers_ids:
                    if self.type == 'individual' or self.pre_paid == True:
                        rec.premium = (rec.rate * self.sum_insured) / 100
                    else:
                        rec.premium = 0.0
                for rec in self.covers_ids:
                        sum+=rec.premium
                self.net_premium=sum




      @api.onchange('net_premium')
      def set_commission(self):
         commission=self.env['commission.table'].search([('lob','=',self.lob.id)])
         if self.net_premium:
              self.broker_commission =(self.net_premium*commission.basic)/100


      def create_endo(self):
            form_view = self.env.ref('e-marine.end_form')

            return {
                  'name': ('Endorsement'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'res_model': 'endorsement.marine',
                  'views': [(form_view.id, 'form')],
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'context': {
                        'default_cover_id': self.id,

                  }
            }
      def _get_stamps(self):
          record_ids=[]
          for rec in self.env['marine.stamps'].search([]):
               id=self.env['policy.stamps'].create({'stamp':rec.id})
               record_ids.append(id.id)
          return record_ids

      is_renewal = fields.Boolean(string="Renewal")
      pre_paid = fields.Boolean(string="Pre-Paid")

      differnce1 = fields.Integer(compute='compute_date', force_save=True)
      today = fields.Date(string="", required=False, compute='todau_comp')
      covers_ids = fields.One2many('policy.covers','policy_id',string="Covers")
      stamp_ids = fields.One2many('policy.stamps','policy_stam_id',string="Stamps",default=_get_stamps)


      # @api.one
      def compute_date(self):
            if self.end_date:
                  # fmt = '%Y-%m-%d'
                  # d1 = datetime.strptime(self.end_date, fmt)
                  # d2 = datetime.strptime(self.today, fmt)
                  daysDiff = str((self.end_date - self.today).days)
                  self.differnce1 = daysDiff

      # @api.one
      def todau_comp(self):
            self.today = datetime.today().strftime('%Y-%m-%d')


      cert_ids=fields.One2many('certificate.marine','open_cover_id',string='Certificates')

      def confirm(self):
            return True

      @api.onchange('sum_insured')
      def get_default_remain(self):
            if self.sum_insured:
                  print("esllllllllllllllllllllllllllllllll")
                  self.remain=self.sum_insured
                  print(self.remain)
      # @api.multi
      def confirm_policy(self):
            if self.cover_num:
                  self.state='approved'
            if self.is_endorsement == True:
                  self.last_cover_id.active=False
                  # print("boss boss boss")
                  # last_confirmed_edit = self.env['policy.marine'].search(
                  #       [('cover_num', '=', self.cover_num),
                  #        ('active', '=', 'True'), ('id', '!=', self.id),
                  #        ('state', '=', 'approved')], )
                  # if last_confirmed_edit:
                  #       last_confirmed_edit.active = False

      def born_dead_policy(self):
            if self.active==False:
                for rec in self.env['policy.marine'].search(['|', ('active', '=', True), ('active', '=', False),('cover_num', '=', self.cover_num)]):
                    if rec.type=='contract':
                        for record in self.env['certificate.marine'].search([('open_cover_id','=',rec.id)]):
                            record.state = 'born-dead'
                            record.net_premium = 0.0
                    rec.state='born-dead'
                    rec.net_premium=0.0
            else:
                self.state = 'born-dead'
                self.net_premium = 0.0
            #       self.state='approved'
            # if self.is_endorsement == True:
            #       self.last_cover_id.active=False
                  # print("boss boss boss")
                  # last_confirmed_edit = self.env['policy.marine'].search(
                  #       [('cover_num', '=', self.cover_num),
                  #        ('active', '=', 'True'), ('id', '!=', self.id),
                  #        ('state', '=', 'approved')], )
                  # if last_confirmed_edit:
                  #       last_confirmed_edit.active = False


      # @api.multi
      def renew_policy(self):
            form_view = self.env.ref('e-marine.form_policy_marine')
            self.active=False
            covers = []
            stamps = []
            for rec in self.covers_ids:
                object = (0, 0, {'cover': rec.cover.id, 'rate': rec.rate, 'premium': rec.premium})
                covers.append(object)
            for rec in self.stamp_ids:
                object = (0, 0, {'stamp': rec.stamp.id, 'value': rec.value})
                stamps.append(object)
            return {
                  'name': ('Policy'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'views': [(form_view.id, 'form')],
                  'res_model': 'policy.marine',
                  'target': 'current',
                  'type': 'ir.actions.act_window',
                  'context': {
                        # "default_discount_party": self.cover_id.discount_party.id,
                        'default_end_date': self.end_date,
                        'default_endorsement_type': self.endorsement_type,
                        'default_cover_num': self.cover_num,
                        'default_in_favour': self.in_favour,
                        'default_ship_from': self.ship_from,
                        'default_agency': self.agency.id,
                        'default_insured': self.insured,
                        'default_marine_type': self.marine_type.id,
                      'default_type': self.type,
                        'default_nature_pakage': [(6, 0, self.nature_pakage.ids)],
                        'default_valution_notes': [(6, 0, self.valution_notes.ids)],
                      'default_broker': self.broker.id,
                      'default_broke_pin': self.broker_pin,

                      'default_broker_fra_code': self.broker_fra_code,

                        'default_rate': self.rate,

                        'default_min_premium': self.min_premium,
                        'default_net_premium': self.net_premium,

                        'default_sum_insured': self.sum_insured,
                        'default_max_per_cert': self.max_per_cert,

                        'default_product': [(6, 0, self.product.ids)],
                      'default_nature_pakage': [(6, 0, self.nature_pakage.ids)],
                      'default_valution_notes': [(6, 0, self.valution_notes.ids)],
                      'default_covers_ids': covers,
                      'default_stamp_ids': stamps,

                        'default_issue_date': self.issue_date,
                        'default_start_date': self.start_date,
                        'default_new_terms': [(6, 0, self.new_terms.ids)],
                        'default_ex_terms_ids': [(6, 0, self.ex_terms_ids.ids)],

                      'default_new_special_terms': [(6, 0, self.new_special_terms.ids)],
                        # 'default_app_date': self.cover_id.app_date,
                        'default_agency_branch': self.agency_branch.id,
                        # 'default_sales_person1': self.cover_id.sales_person1.id,
                        'default_currency_id': self.currency_id.id,
                        'default_is_endorsement': self.is_endorsement,
                        'default_revising_fees': self.revising_fees,
                        # 'default_war': self.war,
                        # 'default_proportional_stamp': self.proportional_stamp,
                        # 'default_dimensional_stamp': self.dimensional_stamp,
                        # 'default_supervisory_stamp': self.supervisory_stamp,
                        # 'default_policy_holder': self.policy_holder,
                        'default_supplier': self.supplier,
                        'default_bank': self.bank,
                        'default_carrier_name': self.carrier_name,
                        'default_consignee': self.consignee,
                        'default_consignee_value': self.consignee_value,
                        'default_invoice_currency': self.invoice_currency.id,
                        'default_invoice_ammount': self.invoice_ammount,
                        'default_conveyance_mode': self.conveyance_mode,
                      'default_address': self.address,

                      'default_is_renewal': True,
                        'default_endorsement_no':self.endorsement_no,
                        'default_is_canceled': self.is_canceled,
                        # 'default_new_risk_ids': records_risks,
                        'default_last_cover_id': self.id,
                        'default_state_track': 'Renewal',

                  },
            }
      # @api.onchange('covers_ids')
      # def changecover(self):
      #     if self.covers_ids:
      #         ids=[]
      #         for rec in self.covers_ids:
      #            ids.append(rec.cover.id)
      #         if any(line for line in self.covers_ids if line.cover.id in ids):
      #         # for rec in self.env['covers'].search([]):
      #         #     for record in self.covers_ids:
      #         #         if record.cover.id==rec.id:
      #                     raise ValidationError('pppppp')

                          # return {'domain': {'covers_ids.cover': [('id', '!=', record.cover.id)]}}

class MarineCovers(models.Model):
    _name = 'policy.covers'
    _rec_name = 'cover'
    cover = fields.Many2one('covers',string='Cover')
    rate = fields.Float(string='Rate')
    premium = fields.Float(string='Premium')
    policy_id= fields.Many2one('policy.marine',string='Policy')
    cert_id= fields.Many2one('certificate.marine',string='Certificate')


    # @api.onchange('cover')
    # def changecover(self):
    #     if self.covers_ids:



    @api.onchange('cover')
    def set_rate(self):
        ids = []
        self.rate=self.cover.rate
        for rec in self.policy_id.covers_ids:
                  ids.append(rec.cover.id)
        if self.cover.id in ids:
            ids.remove(self.cover.id)
            return {'domain': {'cover': [('id', '!=', ids)]}}




class MarineStamps(models.Model):
    _name = 'policy.stamps'
    _rec_name = 'stamp'
    stamp = fields.Many2one('marine.stamps',string='Stamp/Fees')
    value = fields.Float(string='Value')
    policy_stam_id= fields.Many2one('policy.marine',string='Policy')
    cert_id= fields.Many2one('certificate.marine',string='Certificate')







