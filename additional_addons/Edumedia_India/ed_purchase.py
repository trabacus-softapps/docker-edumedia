from openerp.osv import fields,osv
import amount_to_text_softapps

class ed_purchase(osv.osv):
    _description = 'Purchase  Info' 
    _inherit ='purchase.order'
    
    def _amt_in_words(self, cr, uid, ids, fields_name, args, context):
        res={}
        untax_amt = tax = total = 0        
        txt=' Rupees ' 
        
        for case in self.browse(cr, uid, ids):  
           for line in case.order_line:
                untax_amt += line.price_subtotal
                for ln in line.taxes_id:
                    tax += (line.price_subtotal * ln.amount)
           total = untax_amt + tax 
           txt += amount_to_text_softapps._100000000_to_text(int(round(total)))
           txt += ' Only' 
           res[case.id]=txt     
        return res
    
    _columns ={
               'name': fields.char('Order Reference', size=64, readonly=True, select=True, help="unique number of the purchase order,computed automatically when the purchase order is created"),
               'del_pack' : fields.char('Delivery/Packing if any',size=100),
               'del_mode' : fields.char('Delivery Mode',size=50),
               'del_date' : fields.date('Delivery date'),
               'pay_adv' : fields.float('Advance'),
               'pay_bal' : fields.float('Balance'),
               'adv_date' : fields.date('Advance Date'),
               'bal_date' : fields.date('Balance Date'),
               'adv_mode' : fields.char('Mode',size=50),
               'bal_mode' : fields.char('Mode',size=50),
               'penalty_cla' :fields.text('Penality Clause'),
               'reject_cla' : fields.text('Rejection Clause'),
               'amt_words'  : fields.function(_amt_in_words, method=True, string="Amount in Words", type='text', store=True),
               #'pricelist_id':fields.many2one('product.pricelist','Pricelist',required=False),
        
              }

   
ed_purchase() 