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
      insured=fields.Char(related='open_cover_id.insured',string='Customer')

      name=fields.Char('Certificate',readonly=True)
      certificate_num=fields.Char(string='Certificate Num',default=lambda self: self.env['ir.sequence'].next_by_code('certificate'))
      start_date = fields.Date('Effective from')
      end_date = fields.Date('Effective To')
      user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
      agency = fields.Many2one('marine.agency',related='open_cover_id.agency', string='Shipping',store=True)
      agency_branch = fields.Many2one('agency.branch', related='open_cover_id.agency_branch',string='Shipping Branch')
      currency_id=fields.Many2one(related='open_cover_id.currency_id',string='Currency')
      product=fields.Many2many('marine.product',string='Products')
      net_premium = fields.Float('Net Premium',compute='get_prem',store=True)
      war = fields.Float('war',compute='get_prem',store=True)

      sum_insured = fields.Float('Sum Insured')
      rate = fields.Float('Rate',related='open_cover_id.rate',store=True)
      state = fields.Selection([('pending', 'Pending'),
                                ('approved', 'Approved'),
                                ('canceled', 'Canceled'), ],
                               'Status', required=True, default='pending', copy=False)
      issue_fees = fields.Float('Issue Fees')
      proportional_stamp = fields.Float('Proportional Stamp')
      dimensional_stamp = fields.Float('Dimensional Stamp')
      supervisory_stamp = fields.Float('Supervisory Stamp')
      policy_holder = fields.Float('Policy Holder Protection fund')
      revising_fees = fields.Float('Revising and approval fees')
      total = fields.Float('Total',compute='get_total',store=True)
      cert_terms = fields.Many2many(related='open_cover_id.new_terms', string='Terms & Conditions',)
      cert_special_terms = fields.Many2many(related='open_cover_id.new_special_terms', string='Special & Conditions',)

      @api.onchange('net_premium')
      def get_fees(self):
          if self.net_premium:
              self.proportional_stamp = (self.net_premium * .5) / 100
              self.supervisory_stamp = (self.net_premium * .6) / 100
              self.policy_holder = (self.net_premium * .2) / 100
              self.revising_fees = (self.net_premium * .1) / 100

      # @api.one
      @api.depends('issue_fees', 'dimensional_stamp', 'net_premium')
      def get_total(self):
          if self.net_premium:
              self.total = self.issue_fees + self.proportional_stamp + self.dimensional_stamp + self.supervisory_stamp + self.policy_holder + self.revising_fees + self.net_premium


      # @api.one
      @api.depends('sum_insured','rate')
      def get_prem(self):
          if self.rate and self.sum_insured :
              if self.sum_insured <=self.open_cover_id.max_per_cert:
                  self.net_premium=(self.sum_insured*self.rate)
                  self.war=(self.sum_insured*.05)/100

              else:
                  raise exceptions.ValidationError('Sum Insured Should not '
                                                   'exceed the limit of Shipment ')

      # @api.multi
      def confirm_certificate(self):
          if self.sum_insured and self.open_cover_id:
                  print('88888888888888888')
                  self.open_cover_id.remain -= self.sum_insured
          self.state='approved'
          print(self.open_cover_id.remain)


      @api.onchange('open_cover_id')
      def get_product(self):
          if self.open_cover_id:
              return {'domain': {'product': [('id', 'in', self.open_cover_id.product.ids)]}}
