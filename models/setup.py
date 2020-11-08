import xlrd
from xlrd import open_workbook
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models
import xlsxwriter
import io

import base64
from decimal import Decimal
class Agency(models.Model):
    _name = 'marine.agency'
    _rec_name = 'name'
    _description = 'Set up Your Travel Agency'

    name = fields.Char('Agency Name', required=True)
    address = fields.Char('Address')
    email = fields.Char('Email')
    phone = fields.Char('Phone Number')
    mobile = fields.Char('Mobile Number')
    users=fields.One2many('res.users','ship')



class AgencyBranch(models.Model):
    _name = 'agency.branch.marine'
    _rec_name = 'name'
    _description = 'Set up Your Travel Agency Branch'

    name = fields.Char('Branch Name', required=True)
    agency = fields.Many2one('marine.agency', 'Agency',required=True)
    address = fields.Char('Address')
    email = fields.Char('Email')
    phone = fields.Char('Phone Number')
    mobile = fields.Char('Mobile Number')

# class Users(models.Model):
#     _inherit = 'res.users'
#
#     travel_agency = fields.Many2one('travel.agency', 'Travel Agency')
#     travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch',
#                                            domain="[('travel_agency','=',travel_agency)]")
#
#     address = fields.Char('Address')
#     phone = fields.Char('Phone Number')
#     mobile = fields.Char('Mobile Number')
#
#
# class TravelAgencyCommission(models.Model):
#     _name = 'travel.commission'
#     _description = 'Set up Your Travel Commissions'
#
#     travel_agency = fields.Many2one('travel.agency', 'Travel Agency', required=True)
#     valid_from = fields.Date('Valid From', default=datetime.today())
#     valid_to = fields.Date('Valid To', default=datetime.today())
#     commission = fields.Float('Commission Rate')
class Products(models.Model):
     _name = 'marine.product'
     _rec_name = 'name'
     name=fields.Char('Product Name')
     prod_desc=fields.Char('Description')


class Packaging(models.Model):
    _name = 'marine.package'
    _rec_name = 'name'
    name = fields.Char('Package Name')
    desc = fields.Char('Description')
class StampsandFees(models.Model):
    _name = 'marine.stamps'
    _rec_name = 'stamp_name'
    stamp_name= fields.Char('Stamp Name')
    code = fields.Selection([('p-stamp', 'Pro/Stamp'),
                             ('s-stamp', 'SuperVis/Stamp'),
                             ('dim-stamp', 'Dimensional/Stamp'),
                             ('issue-fees', 'Issue/fees'),
                             ], sting='Stamp Code')

    rate = fields.Float('Rate',digits = (12,3))
    stamp_value = fields.Float(sting='Stamp Value')
    type= fields.Selection([('rate', 'Rate'),
                                ('value', 'Fixed Value')],default='rate',sting='Calculation Method')





class Valuation(models.Model):
    _name = 'marine.valuation'
    _rec_name = 'name'
    name = fields.Char('Valuation Name')
    desc = fields.Char('Description')


class TermsandConditions(models.Model):
    _name = 'condition'
    _rec_name = 'term_name'
    term_name = fields.Char('Trem & Condition')
    type = fields.Selection([('basic', 'Basic'),
                                     ('special', 'Special'),
                                     ('exclusion', 'Exclusion'),
                                     ],
                                    string='Type',)
class Covers(models.Model):
    _name = 'covers'
    _rec_name = 'cover_name'
    cover_name = fields.Char('Cover')
    rate = fields.Float(string='Rate',digits = (12,3))
class Users(models.Model):
    _inherit = 'res.users'

    ship = fields.Many2one('marine.agency', 'Shipment')

    # address = fields.Char('Address')
    # phone = fields.Char('Phone Number')
    # mobile = fields.Char('Mobile Number')