from openerp.osv import fields,osv 
from openerp.tools.translate import _
from openerp.addons.Edumedia_India import config
import math

class product_product(osv.osv):
    _inherit='product.product'
    _columns={
              'prod_ids':fields.one2many('ed.product','parent_product_id','Products'),
              'sevice_ids':fields.one2many('ed.service','serv_id','Service'),
              'ed_service_ok': fields.boolean('Include Service'),
              'display_unit' : fields.char('Display Units', size=64, help="Specify the Unit which will be in the Reports")
              }
    _defaults = {
                'ed_service_ok':False
                }
product_product()



class ed_product(osv.osv):
    _name='ed.product'
            
    def _get_tot_quantity(self, cr, uid, ids, field_name, arg, context=None): 
        res = {}
        sale_obj = self.pool.get('sale.order')
        for case in self.browse(cr, uid, ids, context=context): 
            
            cnt_class = studnts = sectns = qty = boys6 = girls6 = boys7 = girls7 = 0
             
            if case.sale_id:
               for sale in sale_obj.browse(cr, uid, [case.sale_id.id]): 
                   if sale.class_ids:
                      for line in sale.class_ids:
                          if line.ed_class == case.ed_class and line.ed_students > 0:
                              cnt_class += 1  
                              studnts += line.ed_students
                              sectns += line.ed_sec
                              if line.ed_class == 6: 
                                  boys6 = line.ed_boys
                                  girls6 = line.ed_girls
                              if line.ed_class == 7: 
                                  boys7 = line.ed_boys
                                  girls7 = line.ed_girls
            if case.ed_per_id:   
                if case.ed_per_id.name == "Class":
                   qty = case.ed_qty * cnt_class
                   
                if case.ed_per_id.name == "Student":
                   qty = case.ed_qty * studnts
                   
                if case.ed_per_id.name == "Section":
                   qty = case.ed_qty * sectns
                
                if case.ed_per_id.name == "Boys" and case.ed_class == 6:
                    qty = case.ed_qty * boys6
                    
                if case.ed_per_id.name == "Boys" and case.ed_class == 7:
                    qty = case.ed_qty * boys7
                    
                if case.ed_per_id.name == "Girls" and case.ed_class == 6:
                     qty = case.ed_qty * girls6
                    
                if case.ed_per_id.name == "Girls" and case.ed_class == 7:
                   qty = case.ed_qty * girls7
                     
                     
            res[case.id] = math.ceil(qty) 
        return res
    
    _columns={
              'parent_product_id':fields.many2one('product.product','Parent Product'),
              'product_id':fields.many2one('product.product','Product', required=True),
              'sale_id':fields.many2one('sale.order','Sale Order'), 
              'ed_qty':fields.float('Quantity', required=True),
              'ed_per_id':fields.many2one('ed.per','PER', required=True),
              'display_unit' : fields.char('Display Units', size=64),
              'ed_class':fields.selection(config.CLASS_STD,'Class'), 
              'tot_quantity' : fields.function(_get_tot_quantity, string="Total Quantity", method=True, store=True, type="float"),
              }
        
    def onchange_product(self, cr, uid, ids, product_id):        
        res = {} 
        
        if product_id :
           product_obj = self.pool.get("product.product").browse(cr, uid, product_id)
           res['display_unit'] = product_obj.display_unit 
        return {'value':res}
    
ed_product()
