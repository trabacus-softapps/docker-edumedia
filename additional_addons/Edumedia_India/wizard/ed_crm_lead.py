from openerp.osv import fields,osv 
from openerp.tools.translate import _
import time


class crm_make_sale(osv.osv_memory):
    _inherit='crm.make.sale'    
    _defaults = { 
         'close': False, 
    }
    
    
    def makeOrder(self, cr, uid, ids, context=None):
        """
        Inherited: to open our customised Sale Order Form
        """
        if context is None:
            context = {}

        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                    
                if False in partner_addr.values():
                    raise osv.except_osv(_('Data Insufficient!'), _('Customer has no addresses defined!'))

                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_order_id': partner_addr['contact'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': time.strftime('%Y-%m-%d'),
                    'fiscal_position': fpos,
                    'ed_type':'so',
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _('Opportunity ') + " '" + case.name + "' "+ _("is converted to Quotation.")
                self.log(cr, uid, case.id, message)
                case_obj._history(cr, uid, [case], _("Converted to Sales Quotation(id: %s).") % (new_id))
                
                
                models_data = self.pool.get('ir.model.data')                
                sale_order_form = models_data._get_id(
                                  cr, uid, 'Edumedia_India', 'view_ed_sale_form')                  
                sale_order_tree = models_data._get_id(
                                  cr, uid, 'Edumedia_India', 'view_ed_sale_tree')
                     
                if sale_order_form:
                    sale_order_form = models_data.browse(
                                      cr, uid, sale_order_form, context=context).res_id
                       
                if sale_order_tree:
                    sale_order_tree = models_data.browse(
                                      cr, uid, sale_order_tree, context=context).res_id
                

            if make.close:
                case_obj.case_close(cr, uid, data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id'  : False,
                    'views'    : [(sale_order_form, 'form'),
                                  (sale_order_tree, 'tree'), ],
                    'type': 'ir.actions.act_window',
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id'  : False,
                    'views'    : [(sale_order_form, 'form'),
                                  (sale_order_tree, 'tree'), ],
                    'type': 'ir.actions.act_window',
                    'res_id': new_ids
                }
            return value

crm_make_sale()  

#class crm_partner2opportunity(osv.osv_memory):
#    """Converts Partner To Opportunity"""
#
#    _name = 'crm.partner2opportunity'
#    _description = 'Partner To Opportunity'
#  