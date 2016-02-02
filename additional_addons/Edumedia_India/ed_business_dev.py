from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.tools
from openerp.osv.orm import except_orm, browse_record
import time


class ed_business_development(osv.osv):
    _name = 'ed.business.development'
    _description = "Business Development"
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']
    _columns = {
        'name'         : fields.char('Name', size=256, required=False, select=True,track_visibility='onchange'),
        'user_id'      : fields.many2one('res.users', 'Business Development Executive', select=True, track_visibility='onchange', ondelete="restrict"),
        'title_action' : fields.char('Explanation', size=500, track_visibility='onchange'),
        'date_action'  : fields.date('Next Action Date', select=True, track_visibility='onchange'),
        'description'  : fields.text('Remarks',track_visibility='onchange'),

        'company_id'     : fields.many2one('res.company', 'Company', ondelete='cascade', select=True, change_default=True),

        'contact_name': fields.char('Contact Name', size=64,track_visibility='onchange'),
        'partner_name': fields.char("School Name", size=64,help='The name of the future partner company that will be created while converting the lead into opportunity', select=1,track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'School', ondelete='set null', track_visibility='onchange',
            select=True, help="Linked partner (optional). Usually created when converting the lead."),
        'title': fields.many2one('res.partner.title', 'Title'),
        'phone': fields.char("Phone", size=64,track_visibility='onchange'),
        'email_from': fields.char('Email', size=128, help="Email address of the contact", select=1,track_visibility='onchange'),

        # Fields for address,
        'street': fields.char('Street',track_visibility='onchange'),
        'street2': fields.char('Street2',track_visibility='onchange'),
        'zip': fields.char('Zip', change_default=True, size=24,track_visibility='onchange'),
        'city': fields.char('City',track_visibility='onchange'),
        'state_id': fields.many2one("res.country.state", 'State',track_visibility='onchange'),
        'country_id': fields.many2one('res.country', 'Country',track_visibility='onchange'),
        'phone': fields.char('Phone',track_visibility='onchange'),
        'fax': fields.char('Fax',track_visibility='onchange'),
        'mobile': fields.char('Mobile',track_visibility='onchange'),

        #ODOO
         'create_date': fields.datetime('Creation Date', readonly=True),

                }

    _order = "date_action desc desc"

    _defaults = {
 'user_id': lambda s, cr, uid, c: uid,
        'date_action': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'crm.lead', context=c),
    }

    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'partner_name': partner.parent_id.name if partner.parent_id else partner.name,
                'contact_name': partner.name if partner.parent_id else False,
                'title': partner.title and partner.title.id or False,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'fax': partner.fax,
                'zip': partner.zip,
                'function': partner.function,
            }
        return {'value': values}

ed_business_development()