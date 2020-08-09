from odoo import api, fields, models


class Endorsement_edit(models.Model):
    _name = "endorsement.marine"
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "endorsement_no"

    cover_id = fields.Many2one("policy.marine", string="Cover",domain="[('state', '=','approved')]")
    endorsement_no = fields.Integer(string="Endorsement Number",compute='get_no')

    # cover_id = fields.Many2one('policy.broker')
    # @api.one
    @api.depends('cover_id')
    def get_no(self):
        if self.cover_id:
            self.endorsement_no=self.cover_id.endorsement_no+1
            # self.end_no='END / ' + str(self.endorsement_no)
    reasonedit = fields.Text(string="Endorsement Discribtion", required=False)
    end_date = fields.Date(string="End Date")
    endorsement_date = fields.Date(string="Endorsement Date")
    converted = fields.Boolean(default=False)
    endorsement_type = fields.Selection([('Technical', 'Technical'),
                                         ('Non Tech', 'Non Tech'),
                                         ('canceled','canceled'),
                                         ('born-dead','Born-Dead'),
                                         ('extend','Extend')],
                                        string='Endorsement Type', required=True)
    is_canceled = fields.Boolean(string="", )




    # @api.multi
    def create_endorsement(self):
        form_view = self.env.ref('e-marine.form_policy_marine')
        if self.endorsement_type == 'canceled':
            print("hena hena hena")
            self.is_canceled = True
        self.converted = True
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
                'default_end_date': self.cover_id.end_date,
                'default_endorsement_type': self.endorsement_type,
                'default_endorsement_no': self.endorsement_no,
                # 'default_end_no': self.end_no,

                'default_cover_num': self.cover_id.cover_num,
                'default_agency': self.cover_id.agency.id,
                'default_rate': self.cover_id.rate,
                'default_insured': self.cover_id.insured,
                'default_cover_type': self.cover_id.cover_type,
                'default_type': self.cover_id.type,

                'default_min_premium': self.cover_id.min_premium,
                'default_net_premium': self.cover_id.net_premium,

                'default_sum_insured': self.cover_id.sum_insured,
                'default_max_per_cert': self.cover_id.max_per_cert,

                'default_product': [(6,0,self.cover_id.product.ids)],
                'default_new_terms': [(6, 0, self.cover_id.new_terms.ids)],
                'default_new_special_terms': [(6, 0, self.cover_id.new_special_terms.ids)],

                'default_issue_date': self.cover_id.issue_date,
                'default_start_date': self.cover_id.start_date,

                # 'default_app_date': self.cover_id.app_date,
                'default_agency_branch': self.cover_id.agency_branch.id,
                # 'default_sales_person1': self.cover_id.sales_person1.id,
                'default_currency_id': self.cover_id.currency_id.id,
                'default_is_endorsement': True,
                'default_is_canceled': self.is_canceled,
                'default_is_renewal': self.cover_id.is_renewal,

                # 'default_new_risk_ids': records_risks,
                'default_last_cover_id': self.cover_id.id,
                'default_state_track': 'Endorsement'

            },
        }
