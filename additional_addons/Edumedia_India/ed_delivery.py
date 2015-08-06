from openerp.osv import fields, osv
from openerp.tools.translate import _
import math
from openerp import netsvc 

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
                'log_partner_id': fields.char('Logistic Partner', size=240),
                'no_boxes': fields.integer('No. Boxes'),
                'docket_no': fields.char('Docket No.', size=100),
                'mode': fields.char('Mode', size=100),
                'weight': fields.char('Weight', size=100),      
                'monthly_id':fields.many2one('ed.monthly.edition','Monthly Edition'),  
                'vw_partner_ids':fields.one2many('vw.res.partner','stock_id','Partner'), 
                'license_detls':fields.char('Details',size=500,readonly=True,states={'draft': [('readonly', False)]}),    
                'service_type':fields.selection([('shl_cinema','School Cinema'),('mentor','Mentor')],'Type',readonly=True,states={'draft': [('readonly', False)]}),
                'user_id':fields.many2one('res.users','Users'),   
                }
    _order = 'id desc'
    
    def print_Labels_Report(self, cr, uid, ids, context=None):
          
       for case in self.browse(cr, uid, ids): 
           
           monthly_edition = 0 
           if case.monthly_id:
               monthly_edition = case.monthly_id.id
           
               cr.execute(""" CREATE OR REPLACE VIEW vw_res_partner AS
                                select r.id,
                                       r.id as partner_id,
                                       """ + str(case.id) + """ as stock_id
                                from res_partner r 
                                where r.id in (select partner_id 
                                        from part_comp_rel 
                                        where comp_id = """+ str(monthly_edition) + """) 
                                order by r.id;""")
                                
               cr.execute(""" CREATE OR REPLACE VIEW vw_ed_subscription AS
                                select s.id,
                                       s.id as subscrib_id,
                                       """ + str(monthly_edition) + """ as monthly_id
                                from ed_subscription s 
                                where s.id in (select subs_id 
                                        from monthly_subs_rel 
                                        where monthly_id = """+ str(monthly_edition) + """) 
                                order by s.id;""")
                                
               cr.execute(""" CREATE OR REPLACE VIEW vw_ed_advertisers AS
                                select ad.id,
                                       ad.id as advertiser_id,
                                       """ + str(monthly_edition) + """ as monthly_id
                                from ed_advertisers_details ad 
                                where ad.id in (select adver_id 
                                        from monthly_adver_rel 
                                        where monthly_id = """+ str(monthly_edition) + """) 
                                order by ad.id;""")
               
               cr.execute(""" CREATE OR REPLACE VIEW vw_ed_director AS
                                select dd.id,
                                       dd.id as director_id,
                                       """ + str(monthly_edition) + """ as monthly_id
                                from ed_director_details dd 
                                where dd.id in (select director_id 
                                        from monthly_direc_rel 
                                        where monthly_id = """+ str(monthly_edition) + """) 
                                order by dd.id;""") 
                       
               self.attach_labels(cr, uid, ids, context)   
                         
       return True      
   
    def print_delvry_order_report(self,cr,uid,ids,context=None):
       """ Button To generate dispatch order for DO"""
       res={}
       sale_obj = self.pool.get('sale.order')
       
       for case in self.browse(cr,uid,ids):
           print case.sale_id
           res = sale_obj.print_order_report(cr,uid,[case.sale_id.id],context)
       return res
    
    
    def attach_labels(self,cr,uid,ids,context=None):
         for case in self.browse(cr,uid,ids): 
           #  self._get_proposal_report(cr, uid, ids, context=None)                      
             data = {}
             data['ids'] = ids 
             data['model'] = 'stock.picking'  
             obj = netsvc.LocalService('report.' + 'monthly.edition.labels')
            
             (result, format) = obj.create(cr, uid, ids, data, context)
            
                       
             doc_parent_id = self.pool.get('document.directory')._get_root_directory(cr,uid)
             attachment_obj = self.pool.get('ir.attachment')
             
             attval = {}
             cr.execute("select id from ir_attachment where res_id = " + str(case.id) + " and res_model = 'stock.picking' and name = '"+ str(case.name) +"-labels.pdf'")
             file_att = cr.fetchall()
             
             if not file_att:
                 attval = {
                        'res_model'  : 'stock.picking',
                        'res_name'   : str(case.name),
                        'res_id'     : str(case.id),
                        'db_datas'   : str(result),
                        'type'       : 'binary',
                        'file_type'  : 'application/pdf',
                        'datas_fname': str(case.name) + "-labels.pdf",
                        'name'       : str(case.name) + "-labels.pdf",
                        'file_size'  : len(result),
                        'parent_id'  : doc_parent_id,
                     }
                 attachment_obj.create(cr,uid,attval)    
             else:
                  for f in file_att:
                     attval = { 
                            'db_datas'   : str(result), 
                            'file_size'  : len(result),
                         }
                     attachment_obj.write(cr,uid, [f[0]],attval) 
         
         return True
                
#       data = {}
#       data['ids'] = ids 
#       data['model'] = 'stock.picking' 
#           
#       return {
#                'report_name': 'monthly.edition.labels',            
#                'type': 'ir.actions.report.xml',            
#                'target': 'new',
#                'datas': data,
#                }
stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns={'ed_remarks':fields.char('Remarks',size=200),}
    
    def create(self, cr, uid, vals, context=None):
        if 'product_qty' in vals:
            vals.update({'product_qty': math.ceil(vals['product_qty'])})
        return super(stock_move, self).create(cr, uid, vals, context=context)
        
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_qty' in vals:
            vals.update({'product_qty': math.ceil(vals['product_qty'])})
        return super(stock_move, self).write(cr, uid, ids, vals, context=context)
    
stock_move()

# class stock_partial_picking(osv.osv_memory):
#     _inherit = "stock.partial.picking"
#     
#     def do_partial(self, cr, uid, ids, context=None):
#         
#         picking_ids= context.get('active_ids', False)
#         picking = self.pool.get('stock.picking').browse(cr,uid,picking_ids[0])
#         for case in self.browse(cr,uid,ids):
#             for op in case.product_moves_out:
#                 if op.quantity > op.product_id.qty_available and picking.type in ('out','internal'):
#                    raise osv.except_osv(_('Warning'),_(str(op.product_id.name_template) + ' Quantity is greater than the Available Stock!!!'))
#             
#             for op in case.product_moves_in:
#                 if op.quantity > op.product_id.qty_available and picking.type in ('out','internal'):
#                    raise osv.except_osv(_('Warning'),_(str(op.product_id.name_template) + ' Quantity is greater than the Available Stock!!!'))
#                
#         super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
#         
#         return {'type': 'ir.actions.act_window_close'}
#         
# stock_partial_picking()
        