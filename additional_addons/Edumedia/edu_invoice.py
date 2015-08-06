# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import re
from datetime import datetime
from dateutil import parser
from openerp import tools
import pytz
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

class edu_payment_detail(osv.osv):
    _name = 'edu.payment.detail' 
    _description = "Payment Detail"
    _columns = {
                'sale_id'  : fields.many2one('sale.order', 'Sale Order'),
                'name'     : fields.char('Payment Type', size=500),
                'bank_name': fields.char('Bank/Branch', size=500),
                'cheque_no': fields.char('DD/Cheque No.', size=500),
                'pay_date' : fields.date('Date'),
                'amount'   : fields.float('Amount', digits_compute=dp.get_precision('Account')),

               }
    
class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
                'no_section': fields.integer('No. Of Sections'),
                'no_boy': fields.integer('No. Of Boys'),
                'no_girl': fields.integer('No. Of Girls'),
                }
    
class sale_order(osv.osv):
    
    _inherit = 'sale.order'
    _columns = {

                'child_partner_ids': fields.many2many('res.partner', 'res_sale_partner_rel', 'sale_id', 'partner_id', 'Contact Person Details'),
                'payment_detail_ids': fields.one2many('edu.payment.detail', 'sale_id', 'Payment Details'),
                'shipping_partner_id' : fields.many2one('res.partner','Shipping Partner')
                }
    
    def print_quotation(self, cr, uid, ids, context=None):
        rep_obj = self.pool.get('ir.actions.report.xml')
        attachment_obj = self.pool.get('ir.attachment')
        for case in self.browse(cr, uid, ids):
            if not case.order_line: 
              raise except_orm(_('No Lines!'), _('Please create some quotation lines.'))
              return False
            self.signal_workflow(cr, uid, ids, 'quotation_sent')
            res = rep_obj.pentaho_report_action(cr, uid, 'account_cusinvoice', ids, None ,None)
            res['datas'].update({'output_type':'pdf'})
            res.update({'name' : case.name and 'Quotation - ' + case.name or 'Quotation'})
        return res
    
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
