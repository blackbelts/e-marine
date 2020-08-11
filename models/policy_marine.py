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
                  type=vals.get('cover_type')
                  currency=vals.get('currency_id')
                  cur = self.env['res.currency'].search([('id','=',currency)]).name
                  vals['cover_num'] = str(type).upper() +'/'+str(cur)+ str(serial_no)
                  return super(PolicyMarine, self).create(vals)

      cover_num=fields.Char('Open Cover',readonly=True)
      insured=fields.Char('Insured')
      in_favour=fields.Char('IN Favour of')
      address=fields.Char('Address')


      issue_date=fields.Date('Issuance Date',default=datetime.today())
      start_date=fields.Date('Effective from',default=datetime.today())

      end_date=fields.Date('Effective To',default=datetime.today())
      active = fields.Boolean(string="Active", default=True)
      min_premium=fields.Float('Limit Net Premium')
      net_premium=fields.Float('Net Premium')
      package_type=fields.Char('Nature of packing')
      inv_num=fields.Char('Order or Invoice No')
      ship_num=fields.Char('Shipping Number')
      file_num=fields.Char('Filing Number')
      trans_means=fields.Char('Conveyance mode')
      ship_from=fields.Char('country origin')
      ship_to=fields.Char('Destination country')





      sum_insured=fields.Float('Sum Insured')
      max_per_cert=fields.Float('Max Per Shipment')
      # terms=fields.Many2many('condition',string='Terms & Conditions' ,domain="[('type', '=', 'basic')]")
      new_terms = fields.Many2many('condition', 'term_cover_rel',  'term_id','cover_id',
                                   string='Terms & Conditions',domain="[('type', '=', 'basic')]")

      new_special_terms=fields.Many2many('condition', 'term_special_cover_rel', 'cover_special_id', 'term_special_id',
                                         string='Terms & Conditions',domain="[('type', '=', 'special')]")

      rate=fields.Float('Rate')
      is_endorsement = fields.Boolean(string="", default=False)
      is_canceled = fields.Boolean(string="", )
      last_cover_id = fields.Many2one('policy.marine', readonly=True)
      endorsement_type = fields.Selection([('Technical', 'Technical'),
                                           ('Non Tech', 'Non Tech'),
                                           ('canceled', 'canceled'),
                                           ('born-dead', 'Born-Dead'),
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


      state_track = fields.Char(default='New')
      remain=fields.Float('Remaining',)
      issue_fees = fields.Float('Issue Fees',default=50)
      war = fields.Float('war')

      proportional_stamp = fields.Float('Proportional Stamp')
      dimensional_stamp = fields.Float('Dimensional Stamp',default=2)
      supervisory_stamp = fields.Float('Supervisory Stamp')
      policy_holder= fields.Float('Policy Holder Protection fund')
      revising_fees = fields.Float('Revising and approval fees')
      total = fields.Float('Total',compute='get_total',store=True)

      @api.onchange('net_premium')
      def get_fees(self):
            if self.net_premium:
                  self.proportional_stamp=(self.net_premium*.5)/100
                  self.supervisory_stamp = (self.net_premium * .6) / 100
                  self.policy_holder = (self.net_premium * .2) / 100
                  self.revising_fees = (self.net_premium * .1) / 100


      # @api.one
      @api.depends('issue_fees', 'dimensional_stamp', 'net_premium')
      def get_total(self):
            if self.net_premium:
                  self.total = self.issue_fees + self.proportional_stamp + self.dimensional_stamp + self.supervisory_stamp+ self.policy_holder+self.revising_fees+ self.net_premium

      state = fields.Selection([('pending', 'Pending'),
                                ('approved', 'Approved'),
                                ('canceled', 'Canceled'), ],
                               'Status', required=True, default='pending', copy=False)

      @api.onchange('sum_insured','rate')
      def compute_net(self):
            if self.sum_insured and self.rate and self.type=='individual':
                  self.net_premium=self.sum_insured*self.rate
                  self.war=(self.sum_insured*.05)/100


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

      is_renewal = fields.Boolean(string="Renewal")
      differnce1 = fields.Integer(compute='compute_date', force_save=True)
      today = fields.Date(string="", required=False, compute='todau_comp')

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

      # @api.multi
      def renew_policy(self):
            form_view = self.env.ref('e-marine.form_policy_marine')
            self.active=False
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
                        'default_agency': self.agency.id,
                        'default_insured': self.insured,
                        'default_cover_type': self.cover_type,
                        'default_type': self.type,

                        'default_rate': self.rate,

                        'default_min_premium': self.min_premium,
                        'default_net_premium': self.net_premium,

                        'default_sum_insured': self.sum_insured,
                        'default_max_per_cert': self.max_per_cert,

                        'default_product': [(6, 0, self.product.ids)],

                        'default_issue_date': self.issue_date,
                        'default_start_date': self.start_date,
                        'default_new_terms': [(6, 0, self.new_terms.ids)],
                        'default_new_special_terms': [(6, 0, self.new_special_terms.ids)],
                        # 'default_app_date': self.cover_id.app_date,
                        'default_agency_branch': self.agency_branch.id,
                        # 'default_sales_person1': self.cover_id.sales_person1.id,
                        'default_currency_id': self.currency_id.id,
                        'default_is_endorsement': self.is_endorsement,
                        'default_is_renewal': True,
                        'default_endorsement_no':self.endorsement_no,
                        'default_is_canceled': self.is_canceled,
                        # 'default_new_risk_ids': records_risks,
                        'default_last_cover_id': self.id,
                        'default_state_track': 'Renewal',

                  },
            }


