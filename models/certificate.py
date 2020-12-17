from datetime import timedelta, datetime
import xlsxwriter
from xlsxwriter.workbook import Workbook
import base64
import xlrd
from xlrd import open_workbook
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models,exceptions
class PolicyMarinecert(models.Model):
      _name='certificate.marine'
      _rec_name = 'name'

      # @api.multi
      # def name_get(self):
      #     if self.open_cover_id:
      #         name=(self.certificate_num + self.open_cover_id.cover_num)
      #     else:
      #         name=(self.certificate_num)
      #
      #     return {'name':name}
      @api.model
      def create(self, vals):
          serial_no = self.env['ir.sequence'].next_by_code('certificate')
          code = self.env['policy.marine']. browse(vals['open_cover_id']).cover_num

          # merge code and serial number
          vals['name'] = str(code) +'/'+ str(serial_no)

          return super(PolicyMarinecert, self).create(vals)

      open_cover_id=fields.Many2one('policy.marine',string='Cover',required=True,domain="[('type', '=', 'contract'),('state', '=', 'approved')]")
      insured=fields.Char(string='Customer')
      in_favour=fields.Char('IN Favour of')
      address=fields.Char(' Insured Address')
      lob = fields.Many2one(related='open_cover_id.lob',string='LOB')
      name=fields.Char('Certificate',readonly=True)
      certificate_num=fields.Char(string='Certificate Num',default=lambda self: self.env['ir.sequence'].next_by_code('certificate'))
      start_date = fields.Date('Effective from')
      end_date = fields.Date('Effective To')
      user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
      agency = fields.Many2one('marine.agency',related='open_cover_id.agency', string='Shipping',store=True)
      agency_branch = fields.Many2one('agency.branch.marine', related='open_cover_id.agency_branch',string='Shipping Branch')
      currency_id=fields.Many2one('res.currency',string='Currency')
      product=fields.Many2many('marine.product',string='Products')
      net_premium = fields.Float('Net Premium',compute='get_prem',store=True)
      war = fields.Float('war',compute='get_prem',store=True)

      sum_insured = fields.Float('Sum Insured')
      rate = fields.Float('Rate',related='open_cover_id.rate',store=True)
      state = fields.Selection([('pending', 'Pending'),
                                ('approved', 'Approved'),
                                ('born-dead', 'Born-dead'),
                                ('canceled', 'Canceled'), ],
                               'Status', required=True, default='pending', copy=False)
      issue_fees = fields.Float('Issue Fees')
      issue_date=fields.Date('Issuance Date',default=datetime.today())

      proportional_stamp = fields.Float('Proportional Stamp')
      dimensional_stamp = fields.Float('Dimensional Stamp')
      supervisory_stamp = fields.Float('Supervisory Stamp')
      policy_holder = fields.Float('Policy Holder Protection fund')
      revising_fees = fields.Float('Revising and approval fees')
      total = fields.Float('Total',compute='get_total',store=True)
      cert_terms = fields.Many2many(related='open_cover_id.new_terms', string='Terms & Conditions',)
      cert_special_terms = fields.Many2many(related='open_cover_id.new_special_terms', string='Special & Conditions',)
      cert_special_terms = fields.Many2many(related='open_cover_id.new_special_terms', string='Special Conditions',)
      cert_ex_terms_ids = fields.Many2many(related='open_cover_id.ex_terms_ids', string='Exclusions',)

      ship_from = fields.Char(related='open_cover_id.ship_from',string='Country origin')
      ship_to = fields.Char(related='open_cover_id.ship_to',string='Destination Country')
      bank = fields.Char('Bank',related='open_cover_id.bank')
      carrier_name = fields.Char('Carrier/Veseel Name',related='open_cover_id.carrier_name')
      supplier = fields.Char('Supplier',related='open_cover_id.supplier')
      consignee = fields.Char('Consignee',related='open_cover_id.consignee')
      consignee_value = fields.Char('Consignee Value',related='open_cover_id.consignee_value')
      invoice_currency = fields.Many2one(related='open_cover_id.invoice_currency', string='Invoice Currency')
      invoice_ammount = fields.Char('Invoice Amount')
      valution_notes = fields.Many2many(related='open_cover_id.valution_notes', string='Valution Notes')
      broker = fields.Many2one(related='open_cover_id.broker_person', string="Broker")
      broker_pin = fields.Char(related='open_cover_id.broker_pin',string="Agent Code")
      broker_fra_code = fields.Char(related='open_cover_id.broker_fra_code',string="Broker FRA Code")
      broker_commission = fields.Float(string="Broker Commission")
      nature_pakage = fields.Many2many(related='open_cover_id.nature_pakage', string='Nature of pakage')
      inv_num = fields.Char('Order or Invoice No',related='open_cover_id.inv_num',)
      ship_num = fields.Char('Shipping Number',related='open_cover_id.ship_num')
      file_num = fields.Char('L/C No',related='open_cover_id.file_num')
      covers_ids = fields.One2many('policy.covers','cert_id',string="Covers",)
      stamp_cert_ids = fields.One2many('policy.stamps','cert_id',string="Stamps")

      @api.model
      def set_stamps(self):
          stamps = {}
          if self.stamp_cert_ids:
              for rec in self.stamp_cert_ids:
                  stamps[rec.stamp.code] = rec.value
          return stamps
      conveyance_mode = fields.Selection( related='open_cover_id.conveyance_mode',string='Conveyance mode')
      @api.onchange('open_cover_id')
      def _get_contract_info(self):
          if self.open_cover_id:
              covers = []
              stamps = []
              for rec in self.open_cover_id.covers_ids:
                  object = (0, 0, {'cover': rec.cover.id, 'rate': rec.rate, 'premium': rec.premium})
                  covers.append(object)
              for rec in self.open_cover_id.stamp_ids:
                  object = (0, 0, {'stamp': rec.stamp.id, 'value': rec.value})
                  stamps.append(object)
              self.insured= self.open_cover_id.insured
              # self.inv_num =self.open_cover_id.inv_num
              # self.agency= self.open_cover_id.agency.id
              # self.rate= self.open_cover_id.rate
              # self.supplier= self.open_cover_id.supplier
              # self.bank= self.open_cover_id.bank
              # self.carrier_name= self.open_cover_id.carrier_name
              # self.consignee= self.open_cover_id.consignee
              # self.consignee_value= self.open_cover_id.consignee_value
              # self.invoice_currency= self.open_cover_id.invoice_currency.id
              # self.invoice_ammount= self.open_cover_id.invoice_ammount
              # # self.address= self.open_cover_id.address
              # self.nature_pakage= [(6, 0, self.open_cover_id.nature_pakage.ids)]
              # self.valution_notes= [(6, 0, self.open_cover_id.valution_notes.ids)],
              self.stamp_cert_ids= stamps
              self.covers_ids=covers

              # self.new_terms= [(6, 0, self.open_cover_id.new_terms.ids)]
              # self.new_special_terms=[(6, 0, self.open_cover_id.new_special_terms.ids)]
              #
              #
              # 'default_app_date': self.open_cover_id.app_date,
              # self.agency_branch=self.open_cover_id.agency_branch.id
              # # 'default_sales_person1': self.open_cover_id.sales_person1.id,
              self.currency_id=self.open_cover_id.currency_id.id
              #
              # self.conveyance_mode=self.open_cover_id.conveyance_mode
              # self.favour=self.open_cover_id.in_favour
              # self.ship_from=self.open_cover_id.ship_from
              # self.ship_to= self.open_cover_id.ship_to
              # self.ship_num= self.open_cover_id.ship_num
              # self.file_num= self.open_cover_id.file_num
              # self.broker=self.open_cover_id.broker.id
              # self.broke_pin= self.open_cover_id.broker_pin
              # self.broker_fra_code=self.open_cover_id.broker_fra_code


              


      # @api.one

      @api.depends('stamp_cert_ids', 'net_premium')
      def get_total(self):
          if self.net_premium and self.stamp_cert_ids:
              sum = 0.0
              for rec in self.stamp_cert_ids:
                  sum += rec.value
              self.total = self.net_premium + sum

      # @api.depends('net_premium')
      # def get_stamps(self):
      #     if self.stamp_cert_ids:
      #         sum = 0.0
      #         for rec in self.stamp_cert_ids:
      #             rec.value=(self.net_premium*rec.stamp.rete)/100

      # @api.one
      @api.onchange('stamp_cert_ids', 'net_premium')
      def set_stamp(self):
          if self.open_cover_id.pre_paid == True:
              pass
          else:
              for rec in self.stamp_ids:
                  if rec.stamp.type == 'rate':
                          rec.value = (rec.stamp.rate * self.net_premium)
                  else:
                          rec.value = rec.stamp.stamp_value

      @api.onchange('sum_insured')
      def get_prem(self):
              if self.covers_ids:
                  for rec in self.covers_ids:
                      rec.premium=(rec.rate*self.sum_insured)/100

              if self.sum_insured <=self.open_cover_id.max_per_cert:
                  sum = 0
                  for rec in self.covers_ids:
                      sum += rec.premium
                  self.net_premium = sum

              else:
                  raise exceptions.ValidationError('Sum Insured Should not '
                                                   'exceed the limit of Shipment ')

      # @api.multi
      def confirm_certificate(self):
          if self.sum_insured and self.open_cover_id:
                  print('88888888888888888')
                  if self.open_cover_id.pre_paid==True:
                      self.open_cover_id.remain -= self.net_premium
                  else:
                     self.open_cover_id.remain -= self.sum_insured
          self.state='approved'
          print(self.open_cover_id.remain)


      @api.onchange('open_cover_id')
      def get_product(self):
          if self.open_cover_id:
              return {'domain': {'product': [('id', 'in', self.open_cover_id.product.ids)]}}

      def born_dead_cert(self):
              self.state='born-dead'

      @api.onchange('net_premium')
      def set_commission(self):
          commission = self.env['commission.table'].search([('lob', '=', self.lob.id)])
          if self.net_premium:
              self.broker_commission = (self.net_premium * commission.basic) / 100