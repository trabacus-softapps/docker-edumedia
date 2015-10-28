from openerp.osv import fields,osv
import amount_to_text_softapps
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import math

class ed_invoice(osv.osv):
    _description = 'Account Invoice  Info' 
    _inherit ='account.invoice'
    
    
    def _amt_in_words(self, cr, uid, ids, fields_name, args, context):
        res={}
        untax_amt = tax = total = 0        
        txt=' Rupees ' 
        
        for case in self.browse(cr, uid, ids):  
           for line in case.invoice_line:
                untax_amt += line.price_subtotal
                for ln in line.invoice_line_tax_id:
                    tax += (line.price_subtotal * ln.amount)
           total = untax_amt + tax 
           txt += amount_to_text_softapps._100000000_to_text(int(round(total)))
           txt += ' Only' 
           res[case.id]=txt     
        return res
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        val1=0
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
                for tax in line.invoice_line_tax_id:
                    val1 += line.total_deposit * tax.amount
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += math.ceil(line.amount)
            
            res[invoice.id]['amount_tax'] += val1   
                
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    
    _columns ={
                'amt_words'  : fields.function(_amt_in_words, method=True, string="Amount in Words", type='text', store=True),
                'sale_id'    : fields.many2one('sale.order','Sale Order'),
                'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
               'term_cond' : fields.text('Terms and Condition'),
               'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True)

              }
    
    def action_move_create(self, cr, uid, ids, *args):
        picking_obj = self.pool.get('stock.picking')
        
        for case in self.browse(cr,uid,ids):
            picking_ids = picking_obj.search(cr,uid,[('sale_id','=',case.sale_id.id),('origin','=',case.sale_id.name)])
            for pick in picking_obj.browse(cr,uid,picking_ids):
                if pick.state != 'done':
                   raise osv.except_osv(_('Warning !'), _('The material pertaining to this sale is not dispatched yet. You cannot validate this invoice.'))
        return super(ed_invoice, self).action_move_create(cr, uid, ids, *args)                      
     
ed_invoice()

class account_invoice_line(osv.osv):
    _inherit='account.invoice.line'
    
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total'] +line.total_deposit
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    
    
    def _get_product_details(self, cr, uid, ids, fields_name, args, context):
        res={}         
        for case in self.browse(cr, uid, ids):                  
            txt = ''   
            if case.invoice_id and case.invoice_id.sale_id:
                    for cl in case.invoice_id.sale_id.class_ids:
                        if cl.films_rate > 0 and case.invoice_id.sale_id.films_only :
                            txt += "Class "  + str(cl.ed_class) + "\n"
                        elif cl.ed_students > 0:
                            if 'school' in case.name.lower().split(): 
                                txt += "Class "  + str(cl.ed_class) + ": "  + str(cl.ed_students) + " Students\n"
                            elif 'films' in case.name.lower().split():
                                txt += "Class "  + str(cl.ed_class) + ": "  + str(cl.ed_students) + " Students\n"                             
                
            res[case.id]=txt     
        return res

    _columns={'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', type="float",
                                digits_compute= dp.get_precision('Account'), store=True),
              'total_deposit':fields.integer('Total Deposit'),
              'product_details':fields.function(_get_product_details, method=True, string="Product Details", type='text', store=True),
              }
   
account_invoice_line()