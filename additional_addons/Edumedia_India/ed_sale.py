from openerp.osv import fields,osv
import time 
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _ 
from openerp import pooler 
from openerp import netsvc 
import base64
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.addons.Edumedia_India import config

class sale_order(osv.osv):
    
    def history(self, cr, uid, cases, keyword, history=False, subject=None, email=False, details=None, email_from=False, message_id=False, attach=[], context=None):
        mailgate_pool = self.pool.get('mailgate.thread')
        return mailgate_pool.history(cr, uid, cases, keyword, history=history,\
                                       subject=subject, email=email, \
                                       details=details, email_from=email_from,\
                                       message_id=message_id, attach=attach, \
                                       context=context)
   
        
    def _get_partner_default_addr(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for case in self.browse(cr, uid, ids, context=context): 
            addr = self.pool.get('res.partner').address_get(cr, uid, [case.partner_id.id], ['default']) 
            res[case.id] = addr['default']
            
        return res
    
     
#    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
#        return super(sale_order,self)._amount_all(cr, uid, ids,field_name,arg,context=context)
            
    def _get_class_details(self, cr, uid, ids, field_name, arg, context=None): 
        res = {}
        for case in self.browse(cr, uid, ids, context=context):
            res[case.id] = {
                            'tot_class': 0, 'low_std': 0, 'high_std': 0, 'tot_student' : 0, 'tot_sectn':0 } 
            
            cnt_class = l_std = h_std = studnts = sectns = 0
            class_std = []
            
            if case.class_ids:
                for line in case.class_ids:
                    cnt_class += 1 
                    class_std.append(line.ed_class)
                    studnts += line.ed_students
                    sectns += line.ed_sec
               
            if class_std:
               l_std = min(class_std)
               h_std = max(class_std)
               
            res[case.id]['tot_class'] = cnt_class
            res[case.id]['low_std'] = l_std
            res[case.id]['high_std'] = h_std
            res[case.id]['tot_student'] = studnts
            res[case.id]['tot_sectn'] = sectns
        return res
   
#    def _get_order(self, cr, uid, ids, context=None):
#        result = {}
#        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
#            result[line.order_id.id] = True
#        return result.keys()
             
    def _get_delivry_ids(self, cr, uid, ids, field_name, arg, context=None):
        
        delivry_obj = self.pool.get("stock.picking")
        res = {}
        for case in self.browse(cr,uid,ids,context):
            res[case.id] = delivry_obj.search(cr, uid, [('sale_id', '=', case.id),('state','=','done')])
            
        return res
                
    _inherit='sale.order'
    _columns={
              # Overridden 
              'product_id': fields.many2one('product.product', 'Product', change_default=True,states={'draft': [('readonly', False)]}), 
#              'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
#                                                store = {
#                                                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
#                                                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
#                                                },
#                                                multi='sums', help="The amount without tax."),
#              'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
#                                            store = {
#                                                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
#                                                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
#                                            },
#                                            multi='sums', help="The tax amount."),
#              'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total',
#                                                store = {
#                                                    'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
#                                                    'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
#                                                },
#                                                multi='sums', help="The total amount."),    
              'state': fields.selection([
                                        ('draft', 'Quotation'),
#                                        ('waiting_date', 'Waiting Schedule'),
#                                        ('proposal_sent', 'Proposal Sent'), 
#                                        ('proposal_accept','Proposal Accepted'),
                                        ('manual', 'Manual In Progress'),
                                        ('progress', 'In Progress'),
                                        ('shipping_except', 'Shipping Exception'),
                                        ('invoice_except', 'Invoice Exception'),
                                        ('done', 'Done'),
                                        ('cancel', 'Cancelled'),
                                        ],'State',readonly=True),
                                        
               # Extra Fields 
              'films_only':fields.boolean('Film License Only',readonly=True ,states={'draft': [('readonly', False)]}),                        
              'address_ids':fields.many2many('res.partner','address_sale_rel','sale_id','address_id','Coordinator Details'),
              'class_ids':fields.one2many('ed.class.details','sale_id','Class Details'),
              'cap1_terms' : fields.char('Caption 1',size=100),
              'cap1_text':fields.text('Caption Text',size=500),
              'cap2_terms' : fields.char('Caption 2',size=100),
              'cap2_text':fields.text('Caption Text',size=500),
              'cap3_terms' : fields.char('Caption 3',size=100),
              'cap3_text':fields.text('Caption Text',size=500),
              'cap4_terms' : fields.char('Caption 4',size=100),
              'cap4_text':fields.text('Caption Text',size=500),
              'ed_type':fields.selection([('so','Sale Order'),('crm','CRM')],'Type'),
              'ed_license':fields.selection(config.CLASS_STD,'License',readonly=True ,states={'draft': [('readonly', False)]}),
              'rsn_reject' : fields.text('Relationship Manager Remarks',readonly=True ,states={'draft': [('readonly', False)]}),
              'ed_proj':fields.char('Project',size=100),
             
              'ed_cdd':fields.integer('No.Of.CDD',readonly=True ,states={'draft': [('readonly', False)]}),
              'ed_rate':fields.integer('Rate',readonly=True ,states={'draft': [('readonly', False)]}),
              'license_rate':fields.integer('Rate',readonly=True ,states={'draft': [('readonly', False)]}),
             
              'nxt_payment_date' : fields.date('Next Payment Date'),
              'licen_stdate' : fields.date('Start Date',readonly=True ,states={'draft': [('readonly', False)]}),
              'licen_eddate' : fields.date('End Date',readonly=True ,states={'draft': [('readonly', False)]}),
              'invoice_id' : fields.many2one('account.invoice','Invoice No',readonly=True),
              
              'training_ids':fields.one2many('ed.training.grid','sale_id','Training'),
              'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model','=',_inherit)]),
              'vw_address_ids':fields.one2many('vw.res.partner','sale_id','View Coordinator Details'),
              'vw_class_ids':fields.one2many('vw.ed.class.details','sale_id','view class details'),              
              'payment_ids' : fields.one2many('ed.payment','sale_id','ed.payment'),
              'feedback_ids':fields.one2many('ed.feedback','sale_id','Feedback'),
               
              'ed_pod_ids':fields.one2many('ed.product','sale_id','Product',states={'draft': [('readonly', False)]}),
              'ed_serv_ids':fields.one2many('ed.service','sale_id','service',states={'draft': [('readonly', False)]}),
              'hub_id' : fields.many2one('ed.hub','HUB',readonly=True,states={'draft': [('readonly', False)]}),
              'partner_default_id': fields.function(_get_partner_default_addr, method=True, relation='res.partner', type="many2one", string='Default Contact', strore=True),
                
              'tot_class' : fields.function(_get_class_details, string="Total Classes", method=True, store=True, type="integer", multi="class_details"),
              'low_std' : fields.function(_get_class_details, string="Lowest Standard", method=True, store=True, type="integer", multi="class_details"),
              'high_std' : fields.function(_get_class_details, string="Highest Standard", method=True, store=True, type="integer", multi="class_details"),
              'tot_student' : fields.function(_get_class_details, string="Total Students", method=True, store=True, type="integer", multi="class_details"),
              'tot_sectn' : fields.function(_get_class_details, string="Total Sections", method=True, store=True, type="integer", multi="class_details"),
               'delivery_ids': fields.function(_get_delivry_ids, method=True, type='one2many', obj='stock.picking', string='Delivery Orders' ,readonly=True),
              
                  
} 
 

    def _create_session(self, cr, uid, ids, context=None):
       ses_obj = self.pool.get('ed.sessions')
        
       for case in self.browse(cr, uid, ids):
           ses_vals={
                     'sale_id':case.id,
                     'ed_so': case.name,
                     'ed_school':case.partner_id.name,
                    }
           
           ses_obj.create(cr, uid,ses_vals)
            
       return True
    
    def _open_crm_form(self, cr, uid, ids, context=None):
        
        
        models_data = self.pool.get('ir.model.data')                
        sale_order_form = models_data._get_id(
                          cr, uid, 'Edumedia_India', 'view_ed_sale_crm_form')                  
        sale_order_tree = models_data._get_id(
                          cr, uid, 'Edumedia_India', 'view_ed_sale_tree')
             
        if sale_order_form:
            sale_order_form = models_data.browse(
                              cr, uid, sale_order_form, context=context).res_id
               
        if sale_order_tree:
            sale_order_tree = models_data.browse(
                              cr, uid, sale_order_tree, context=context).res_id
         
                             
        return   { 
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id'  : False,
                    'views'    : [(sale_order_form, 'form'),
                                  (sale_order_tree, 'tree'), ],
                    'type': 'ir.actions.act_window',
                    'res_id': ids[0]
                }
        
    
                
#   *************** Overwritten standard function ***************** 

    def action_wait(self, cr, uid, ids, *args):
        self.button_dummy(cr, uid, ids)
        for o in self.browse(cr, uid, ids):
            if (o.order_policy == 'manual'):
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': time.strftime('%Y-%m-%d')})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': time.strftime('%Y-%m-%d')})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
            message = _("The quotation '%s' has been converted to a sales order.") % (o.name,)
            self.log(cr, uid, o.id, message)
            self._create_session(cr, uid, ids)
            
            partner_obj = self.pool.get('res.partner')
            partner_obj.write(cr,uid,[o.partner_id.id],{'ed_sh_cinema':True})
            
#            self._open_crm_form(cr, uid, ids)

        return True
    
    
    def button_2populateLines(self, cr, uid, ids, context=None):
        ordln_obj = self.pool.get('sale.order.line')
        edProd_obj = self.pool.get('ed.product')
        edServ_obj = self.pool.get('ed.service')
        class_obj = self.pool.get('ed.class.details') 
        prod_obj = self.pool.get('product.product')
        
        prod_id = []
        
        for case in self.browse(cr, uid, ids):
            
            cr.execute("delete from sale_order_line where order_id = %d"%(case.id))
            cr.execute("delete from ed_product where sale_id = %d"%(case.id))
            cr.execute("delete from ed_service where sale_id = %d"%(case.id))
            cr.execute("delete from address_sale_rel where sale_id=%d"%(case.id))
            
            prod_films = prod_obj.search(cr,uid,[('name_template','=','Films')],limit=1)
            prod_license = prod_obj.search(cr,uid,[('name_template','=','License')],limit=1)
            prod_id.append(case.product_id.id)
            if prod_films:
               prod_id.append(prod_films[0])
            if prod_license:
               prod_id.append(prod_license[0])
               
            # to create sale order lines on select of product
            for prod in self.pool.get('product.product').browse(cr,uid,prod_id):
                
                result = ordln_obj.product_id_change(cr, uid, ids, case.pricelist_id.id, prod.id, qty=0,
                                        uom=False, qty_uos=0, uos=False, name='', partner_id=case.partner_id.id,
                                        lang='lang' in context and context.get('lang')or False, update_tax=True, date_order=case.date_order, packaging=False, fiscal_position=False, flag=False)
                
                prod_name = ''
                if prod.name == 'Films':
                   prod_name = str(prod.name) + ' - License Fee'
                    
                lnvals = {
                     'product_id':prod.id,
                     'product_uom':prod.uom_id.id, 
                     'name':prod_name or prod.name,
                     'price_unit':prod.list_price,
                     'order_id':case.id,
                     'tax_id' :[(6, 0, result['value']['tax_id'])],
                     }
                ordln_id = ordln_obj.create(cr, uid, lnvals) 
                
                #to create lines of subproducts and service of main product   
                if prod.prod_ids:
                    for subprod in prod.prod_ids: 
                        edProd_obj.create(cr, uid, {
                                'product_id':subprod.product_id.id,
                                'ed_qty': subprod.ed_qty,
                                'ed_per_id':subprod.ed_per_id.id,
                                'ed_class':subprod.ed_class,
                                'display_unit':subprod.product_id.display_unit,
                                'sale_id':case.id
                            }) 
                        
                    for serv in prod.sevice_ids:
                        edServ_obj.create(cr, uid, {
                                'name':serv.name,
                                'sale_id':case.id
                                })   
                ordln_obj.write(cr,uid,[ordln_id],{})
            
            #to create lines of address for selected customer             
            for add in case.partner_id.address:
                if add.type == 'contact':
                   
                   cr.execute("insert into address_sale_rel(sale_id, address_id) values(%d,%d)"%(case.id, add.id))               
            
            #to create class lines 
            if not case.class_ids:
                   for i in range(1,9):
                       class_obj.create(cr,uid,{'sale_id' : case.id,
                                                'ed_class' : i,
                                                'ed_boys':0,
                                                'ed_girls':0,
                                                'ed_sec':0,
                                                'ed_students':0
                                               },context)     
        return True 
    
#    ************************************ button to generate sale Dispatch order report***************************    

    def print_order_report(self, cr, uid, ids, context=None):
          
       for case in self.browse(cr, uid, ids): 
           cr.execute(""" CREATE OR REPLACE VIEW vw_res_partner_address AS
                            select pa.id
                                  , pa.name
                                  , pa.mobile
                                  , pa.email
                                  , pa.ed_desig_id
                                  , """ + str(case.id) + """ as sale_id
                            from res_partner_address pa
                            where pa.id in (select address_id from address_sale_rel 
                                        where sale_id =  """ + str(case.id) + """);
                                        
                        CREATE OR REPLACE VIEW vw_ed_class_details AS
                            select cl.id
                                  , cl.ed_class    
                                  , cl.ed_sec
                                  , cl.ed_students
                                  , cl.ed_boys
                                  , case when cl.ed_class = 6 then sum(cl.ed_girls)
                            else 0 end as girls
                      , case when cl.ed_class = 7 then sum(cl.ed_boys)
                            else 0 end as boys
                                  , cl.ed_girls
                                  , """ + str(case.id) + """  as sale_id
                            from ed_class_details cl
                            where cl.id in (select cls_id from class_sale_rel 
                                        where sale_id = """ + str(case.id) + """)
                             group by cl.id,cl.ed_class ,cl.ed_sec, cl.ed_students, cl.ed_boys, cl.ed_girls """);          
                
       data = {}
       data['ids'] = ids 
       data['model'] = 'sale.order' 
           
       return {
                'report_name': 'sale.order.dispatch.order',            
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }
    
    
    def print_proposal_report(self, cr, uid, ids, context=None):
       """ button to generate proposal report """           

    #   self._get_proposal_report(cr, uid, ids, context=None)                      
       data = {}
       data['ids'] = ids 
       data['model'] = 'sale.order' 
           
       return {
                'report_name': 'sale.order.proposal',            
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }  

    # Modifying Standard Shipping create from Sale Order 
    # to create deliveries for school cinema process  
    def action_ship_create(self, cr, uid, ids, *args):
        wf_service = netsvc.LocalService("workflow")
        prod_obj = self.pool.get('product.product')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids, context={}):
            proc_ids = []
            output_id = order.shop_id.warehouse_id.lot_output_id.id
 
        val = {}

        val['ed_type']='crm'             
        self.write(cr, uid, [order.id], val)
        return True 
    
    
    def _create_delivery_order(self, cr, uid, ids, context=None): 
        
        picking_id = False
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        prod_obj = self.pool.get('product.product')
        
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        
        for order in self.browse(cr, uid, ids, context={}):
            proc_ids = []
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            picking_id = move_id = False
            cls_txt1 = ''
            
            count = 0
            for line in order.order_line:
                count += 1
                proc_id = False
                
                date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
                date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')
                
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    location_id = order.shop_id.warehouse_id.lot_stock_id.id
                    if not picking_id and line.product_id == order.product_id and line.price_unit > 0:
                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'name': pick_name,
                            'origin': order.name,
                            'type': 'out',
                            'state': 'draft',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                            'company_id': order.company_id.id,
                            'service_type':'shl_cinema'                                             
                        })
                        
                    #Selecting the no of classes, sections and students
                    nof_class = nof_sec = nof_stud = 0
                    cr.execute('SELECT count(c.ed_class) as cls_count, sum(ed_sec) as sec, sum(ed_students) as stud FROM ed_class_details c  WHERE c.sale_id = %d'%(order.id)) 
                    cls = cr.fetchone()
                    if cls:
                      if cls[0] == 0:
                          raise osv.except_osv(_('Warning'),_("Add Data in other details"))  
                      nof_class = cls[0]
                      nof_sec = cls[1]
                      nof_stud = cls[2]
                       
                    #Looping through sub products against the option selected
                    cls_txt = ''
                    if not move_id:    
                        for cl in order.class_ids:                        
                            if cl.ed_students > 0 and cl.wrk_bk_rate > 0 :
                                cls_txt += str(cl.ed_class) + ','
                                for subprod in order.ed_pod_ids: 
                                    qty = 0
                                    if subprod.ed_class == cl.ed_class:   
                                        if subprod.ed_per_id.name == 'Student':
                                           qty = cl.ed_students * subprod.ed_qty
                                        if subprod.ed_per_id.name == 'Class':
                                           qty = nof_class * subprod.ed_qty  
                                        if subprod.ed_per_id.name == 'Section':
                                           qty = cl.ed_sec * subprod.ed_qty 
                                        if subprod.ed_per_id.name == 'Boys' and cl.ed_boys > 0 :
                                           qty = cl.ed_boys * subprod.ed_qty   
                                        if subprod.ed_per_id.name == 'Girls' and cl.ed_girls > 0 :
                                           qty = cl.ed_girls * subprod.ed_qty
                                        
                                        #if subprod.ed_per_id.name:
                                        if qty > 0:               
                                            move_id = self.pool.get('stock.move').create(cr, uid, {
                                                    'name': line.name[:64],
                                                    'picking_id': picking_id,
                                                    'product_id': subprod.product_id.id,
                                                    'date': date_planned,
                                                    'date_expected': date_planned,
                                                    'product_qty': qty,
                                                    'product_uom': subprod.product_id.uom_id.id,
                                                    'product_uos_qty': qty,
                                                    'product_uos': subprod.product_id.uom_id.id,
                                                    #'product_packaging': line.product_packaging.id,
                                                    #'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                                                    'location_id': location_id,
                                                    'location_dest_id': output_id,
                                                    'sale_line_id': line.id,
                                                    'tracking_id': False,
                                                    'state': 'draft',
                                                    #'state': 'waiting',
                                                    'note': line.notes,
                                                    'company_id': order.company_id.id,
                                                })
                        
                        #updating license details to stock picking
                        cls_txt = cls_txt[0:(len(cls_txt) - 1)]
                        if picking_id:
                           self.pool.get('stock.picking').write(cr, uid, [picking_id],{'license_detls':"License Start Date :" + str(order.licen_stdate) + 
                                                                                                       ", License End Date :" + str(order.licen_eddate) +
                                                                                                       ", Class :"              + cls_txt})               
                    
                    if count == 3:  
                        cls_txt = ''
                        for cl in order.class_ids:                        
                            if cl.films_rate > 0 :
                               cls_txt += str(cl.ed_class) + ','  
                        cls_txt = cls_txt[0:(len(cls_txt) - 1)]    
                        # creating additional deliver order for HDD media
                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'name': pick_name,
                            'origin': order.name,
                            'type': 'out',
                            'state': 'draft',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                            'company_id': order.company_id.id,
                            'license_detls' :"License Start Date :" + str(order.licen_stdate) + 
                                                            ", License End Date :" + str(order.licen_eddate) +
                                                            ", Class :"              + cls_txt,
                            'service_type':'shl_cinema'              
                        })
                                            
                        products = prod_obj.search(cr,uid,[('categ_id', '=', 'HDD')],limit=1)
                        
                        for prod in prod_obj.browse(cr,uid,products):
                            move_id = self.pool.get('stock.move').create(cr, uid, {
                                'name': line.name[:64],
                                'picking_id': picking_id,
                                'product_id': prod.id,
                                'date': date_planned,
                                'date_expected': date_planned,
                                'product_qty': order.ed_cdd,
                                'product_uom': prod.uom_id.id,
                                'product_uos_qty': order.ed_cdd,
                                'product_uos': prod.uom_id.id,
                                #'product_packaging': line.product_packaging.id,
                                #'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                                'location_id': location_id,
                                'location_dest_id': output_id,
                                'sale_line_id': line.id,
                                'tracking_id': False,
                                'state': 'draft',
                                #'state': 'waiting',
                                'note': line.notes,
                                'company_id': order.company_id.id,
                            })
                            
                if line.product_id:
                    proc_id = self.pool.get('procurement.order').create(cr, uid, {
                        'name': line.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': (line.product_uos and line.product_uos_qty)\
                                or line.product_uom_qty,
                        'product_uos': (line.product_uos and line.product_uos.id)\
                                or line.product_uom.id,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                        'move_id': move_id,
                        'property_ids': [(6, 0, [x.id for x in line.property_ids])],
                        'company_id': order.company_id.id,
                    })
                    proc_ids.append(proc_id)
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
                    if order.state == 'shipping_except':
                        for pick in order.picking_ids:
                            for move in pick.move_lines:
                                if move.state == 'cancel':
                                    mov_ids = move_obj.search(cr, uid, [('state', '=', 'cancel'),('sale_line_id', '=', line.id),('picking_id', '=', pick.id)])
                                    if mov_ids:
                                        for mov in move_obj.browse(cr, uid, mov_ids):
                                            move_obj.write(cr, uid, [move_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
                                            proc_obj.write(cr, uid, [proc_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
                                            
                                            
            if order.state == 'shipping_except':
                val['state'] = 'progress'
                val['shipped'] = False
                
                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
        return True
    
    #inherited
    def _make_invoice(self, cr, uid, order, lines, context=None):
        
        accinv_obj = self.pool.get('account.invoice')
        invln_obj = self.pool.get('account.invoice.line')
        res = super(sale_order, self)._make_invoice(cr, uid, order,lines, context=context)
        accinv_obj.write(cr,uid,[res],{'sale_id':order.id})
        invln_ids = invln_obj.search(cr,uid,[('invoice_id','=',res)])
        invln_obj.write(cr,uid,invln_ids,{})
        return res
        
    # Overridden
    def manual_invoice(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        inv_ids = set()
        inv_ids1 = set()
        for id in ids:
            for record in self.pool.get('sale.order').browse(cr, uid, id).invoice_ids:
                inv_ids.add(record.id)
                
        # inv_ids would have old invoices if any
        for id in ids:
            wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
            for record in self.pool.get('sale.order').browse(cr, uid, id).invoice_ids:
                inv_ids1.add(record.id)
        inv_ids = list(inv_ids1.difference(inv_ids))

        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        
        
        self.write(cr, uid, [id], {'invoice_id':inv_ids[0]})        
        
        self._create_delivery_order(cr, uid, ids, context)
        return True
    
    #overriden
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_inv = False, context=None):
        res = False
        invoices = {}
        invoice_ids = []
        picking_obj = self.pool.get('stock.picking')
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        if context is None:
            context = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_inv:
            context['date_inv'] = date_inv
        for o in self.browse(cr, uid, ids, context=context):
            lines = []
            for line in o.order_line:
                if line.price_unit > 0:
                    if line.invoiced:
                        continue
                    elif (line.state in states):
                        lines.append(line.id)
            created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                invoice_ref = ''
                for o, l in val:
                    invoice_ref += o.name + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    if o.order_policy == 'picking':
                        picking_obj.write(cr, uid, map(lambda x: x.id, o.picking_ids), {'invoice_state': 'invoiced'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                invoice.write(cr, uid, [res], {'origin': invoice_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    for lin in il:#to split sale order lines and create seprate invoices
                        res = self._make_invoice(cr, uid, order, [lin], context=context)
                        invoice_ids.append(res)
                        self.write(cr, uid, [order.id], {'state': 'progress'})
                        if order.order_policy == 'picking':
                            picking_obj.write(cr, uid, map(lambda x: x.id, order.picking_ids), {'invoice_state': 'invoiced'})
                        cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
        return res

        
    # Overridden
    def button_dummy(self, cr, uid, ids, context=None):
        ordln_obj=self.pool.get('sale.order.line')
        edprod_obj=self.pool.get('ed.product')
        
        for case in self.browse(cr,uid,ids):
            if case.order_line:
                for line in case.order_line:
                    ordln_obj.write(cr,uid,[line.id],{})
                    
            if case.ed_pod_ids:
                for ep in case.ed_pod_ids:    
                    edprod_obj.write(cr, uid, [ep.id], {})     
            self.write(cr, uid, [case.id], {})        
        return True 
    
    def button_proposal_sent(self,cr,uid,ids,context=None):
         for case in self.browse(cr,uid,ids): 
           #  self._get_proposal_report(cr, uid, ids, context=None)                      
             data = {}
             data['ids'] = ids 
             data['model'] = 'sale.order'  
             obj = netsvc.LocalService('report.' + 'sale.order.dispatch.order')
            
             (result, format) = obj.create(cr, uid, ids, data, context)
            
                       
             doc_parent_id = self.pool.get('document.directory')._get_root_directory(cr,uid)
             attachment_obj = self.pool.get('ir.attachment')
             
             attval = {}
             cr.execute("select id from ir_attachment where res_id = " + str(case.id) + " and res_model = 'sale.order' and name = '"+ str(case.name) +".pdf'")
             file_att = cr.fetchall()
             
             if not file_att:
                 attval = {
                        'res_model'  : 'sale.order',
                        'res_name'   : str(case.name),
                        'res_id'     : str(case.id),
                        'db_datas'   : str(result),
                        'type'       : 'binary',
                        'file_type'  : 'application/pdf',
                        'datas_fname': str(case.name) + ".pdf",
                        'name'       : str(case.name) + ".pdf",
                        'file_size'  : len(result),
                        'parent_id'  : doc_parent_id,
                        'partner_id' : case.partner_id.id,
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
     
    def button_proposal_accepted(self,cr,uid,ids,context=None):        
         self.write(cr, uid, ids, {'state':'proposal_accept'})         
         return True
     
    def _open_sale_form(self, cr, uid, ids, context=None):
        
        
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
        return   { 
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id'  : False,
                    'views'    : [(sale_order_form, 'form'),
                                  (sale_order_tree, 'tree'), ],
                    'type': 'ir.actions.act_window',
                    'res_id': ids[0]
                }
     
     # Overridden:
    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        
        for sale in self.browse(cr, uid, ids):
            if sale.state == 'cancel':                
                    l = len(sale.name)
                    
                    if l > 5:
                        nxt_no = int(sale.name[8:(l-1)]) + 1
                        
                        sale_name = sale.name[0:8] + str(nxt_no) +  sale.name[(l-1):l] 
                    else:  
                        sale_name = str(sale.name) + ' (R1)' 
                    
                    self.write(cr, uid, ids, {'state': 'draft','ed_type':'so','name':sale_name, 'invoice_ids': [], 'shipped': 0})
            else:   
                    self.write(cr, uid, ids, {'state': 'draft','ed_type':'so', 'invoice_ids': [], 'shipped': 0})
                
        cr.execute('select id from sale_order_line where order_id IN %s and state=%s', (tuple(ids), 'cancel'))
        line_ids = map(lambda x: x[0], cr.fetchall())
        self.pool.get('sale.order.line').write(cr, uid, line_ids, {'invoiced': False, 'state': 'draft', 'invoice_lines': [(6, 0, [])]})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            # Deleting the existing instance of workflow for SO
            wf_service.trg_delete(uid, 'sale.order', inv_id, cr)
            wf_service.trg_create(uid, 'sale.order', inv_id, cr)
        for (id,name) in self.name_get(cr, uid, ids):
            message = _("The sales order '%s' has been set in draft state.") %(name,)
            self.log(cr, uid, id, message)
            
   #     self._open_sale_form(cr, uid, ids)
            
        return True
        
     
    # Overridden:
    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        proc_obj = self.pool.get('procurement.order')
        
        for sale in self.browse(cr, uid, ids, context=context):
            for pick in sale.picking_ids:
                if pick.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Could not cancel sales order !'),
                        _('You must first cancel all picking attached to this sales order.'))
                if pick.state == 'cancel':
                    for mov in pick.move_lines:
                        proc_ids = proc_obj.search(cr, uid, [('move_id', '=', mov.id)])
                        if proc_ids:
                            for proc in proc_ids:
                                wf_service.trg_validate(uid, 'procurement.order', proc, 'button_check', cr)
                                
            for r in self.read(cr, uid, ids, ['picking_ids']):
                for pick in r['picking_ids']:
                    wf_service.trg_validate(uid, 'stock.picking', pick, 'button_cancel', cr)
                    
            for inv in sale.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Could not cancel this sales order !'),
                        _('You must first cancel all invoices attached to this sales order.'))
                    
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
                    
            sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line],
                    {'state': 'cancel'})
            
            message = _("The sales order '%s' has been cancelled.") % (sale.name,)
            self.log(cr, uid, sale.id, message)
        
            if sale.ed_type == 'crm':
                
                 cr.execute("delete from ed_sessions where sale_id = %d"%(sale.id))
                 
        self.write(cr, uid, ids, {'state': 'cancel','ed_type':'so'})
            
        return True 
    
    def write(self, cr, uid, ids,vals,context=None):
        addr_obj = self.pool.get('res.partner')
        partner_obj = self.pool.get('res.partner')
        class_obj = self.pool.get('ed.class.details')
        line_obj = self.pool.get('sale.order.line')         
        
        result = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        for case in self.browse(cr, uid, ids):
            if case.address_ids:
                for a in case.address_ids:
                    if not a.partner_id:
                        addr_obj.write(cr, uid, [a.id], {'partner_id': case.partner_id.id})
                        
#            sale_cls_ids = set()         
#            if case.class_ids:
#                for c in case.class_ids:
#                    sale_cls_ids.add(c.id) 
#                  
#            part_cls_ids = new_cls_ids = set()
#                          
#            partner = partner_obj.browse(cr,uid, case.partner_id.id)
#            for pc in partner.ed_cls_ids:                
#                part_cls_ids.add(pc.id) 
#            new_cls_ids = sale_cls_ids - part_cls_ids   
            
#            class_ids = class_obj.search(cr,uid,[('sale_id','=',case.id)],order='ed_class')
            
            tot_wb_price = tot_fl_price = avg_wb_price =  avg_fl_price = 0.00
            tot_stu = 0
            id 
            for cl in case.class_ids:
                if not case.films_only:
                    tot_wb_price += cl.wrk_bk_rate * cl.ed_students
                    tot_fl_price += cl.films_rate * cl.ed_students
                    tot_stu += cl.ed_students
                
                if case.films_only:
                   tot_fl_price += cl.films_rate 
            
            avg_wb_price = tot_wb_price / (tot_stu or 1)
            avg_fl_price = tot_fl_price / (tot_stu or 1)
            
            lvals = {}
            line_ids = line_obj.search(cr,uid,[('order_id','=',case.id)])
            for ln in line_obj.browse(cr,uid,line_ids):
                if ln.product_id.name_template == case.product_id.name:
                   lvals = {'price_unit':avg_wb_price,'ed_units':case.ed_cdd,'ed_per_depo':0}
                if ln.product_id.name_template == 'Films':                    
                   lvals = {'price_unit':avg_fl_price} 
                if ln.product_id.name_template == 'License':
                   lvals = {'price_unit':case.license_rate}   
                line_obj.write(cr,uid,[ln.id],lvals)
            #partner_obj.write(cr, uid, [partner.id], {'ed_cls_ids': [(6, 0, new_cls_ids)]})
#            for n in new_cls_ids: 
#                cr.execute("insert into ed_partner_cls_rel(partner_id, class_id) values(%d,%d)"%(case.partner_id.id, n))
        return result
    
sale_order()

class sale_order_line(osv.osv):
    _inherit='sale.order.line'

#    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
#        tax_obj = self.pool.get('account.tax')
#        cur_obj = self.pool.get('res.currency')
#        res = {}
#        if context is None:
#            context = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            price =  line.price_unit * (1 - (line.discount or 0.0) / 100.0) 
#            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price,line.product_uom_qty ,line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
#             
#            cur = line.order_id.pricelist_id.currency_id
#            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']+line.ed_total)
#        return res
    
    def get_deposit_Total(self,cr,uid,ids,field_name,arg,context=None):       
        res = {}
        sale_obj = self.pool.get('sale.order')
        for case in self.browse(cr,uid,ids):  
            deposit = 0.00
            if case.order_id:
                sale = sale_obj.browse(cr,uid,case.order_id.id) 
                deposit = sale.ed_cdd * sale.ed_rate            
            res[case.id] = deposit             
        return res
    
    def _get_students(self,cr,uid,ids,field_name,arg,context=None):
        
        res={}
        for case in self.browse(cr, uid, ids):
            res[case.id]= 1
            if case.product_id.name != 'License' and not case.order_id.films_only:
                cr.execute('SELECT sum(ed_students) as stud FROM ed_class_details c \
                            WHERE c.sale_id =%d'%(case.order_id.id)) 
                cls = cr.fetchone()
                res[case.id]= cls and cls[0] or 1        
        return res
        
        
    def _default_qty(self, cr, uid, context=None):   
        sale_id = context.get('sale_id', False) 
        if sale_id:
           cr.execute('SELECT sum(ed_students) as stud FROM ed_class_details c \
                       WHERE c.sale_id =%d'%(sale_id)) 
           cls = cr.fetchone()
           return cls and cls[0] or 1
        else:
            return 1   
    
    _columns={
              # Inherited
#             'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),        
#              'ed_total':fields.function(get_deposit_Total, method=True, string='Total Deposit', type='float', store=True, readonly=True),
              'product_uom_qty':fields.function(_get_students, method=True, string='NO.Of Students', type='float', store=True),
              'ed_units':fields.integer('No.Of.Units'),
              'ed_per_depo':fields.integer('Deposit Per Unit'),
              'notes': fields.text('Notes'),
              }
    _defaults={
               'product_uom_qty':_default_qty
               }
    _order = 'id'
    
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('procurement.order').quantity_get(cr, uid,
                        line.procurement_id.id, context=context)

        def _get_line_uom(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('procurement.order').uom_get(cr, uid,
                        line.procurement_id.id, context=context)

        create_ids = []
        sales = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.invoiced:
                if line.product_id:
                    a = line.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = line.product_id.categ_id.property_account_income_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'),
                                _('There is no income account defined ' \
                                        'for this product: "%s" (id:%d)') % \
                                        (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    a = prop and prop.id or False
                uosqty = _get_line_qty(line)
                uos_id = _get_line_uom(line)
                pu = 0.0
                if uosqty:
                    pu = round(line.price_unit * line.product_uom_qty / uosqty,
                            self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
                fpos = line.order_id.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                if not a:
                    raise osv.except_osv(_('Error !'),
                                _('There is no income category account defined in default Properties for Product Category or Fiscal Position is not defined !'))
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'origin': line.order_id.name,
                    'account_id': a,
                    'price_unit': pu,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                    'note': line.notes,
                    'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced': True})
                sales[line.order_id.id] = True
                create_ids.append(inv_id)
        # Trigger workflow events
        wf_service = netsvc.LocalService("workflow")
        for sid in sales.keys():
            wf_service.trg_write(uid, 'sale.order', sid, cr)
        return create_ids

    
    def onchange_Total(self, cr, uid, ids, ed_per_depo,ed_units):        
        res = {}
        total_dep = 0
        
        if ed_per_depo and ed_units:
              total_dep = ed_per_depo * ed_units
              
              res['ed_total'] = total_dep
              
        return {'value':res}
    
#    def onchange_subtotal(self, cr, uid, ids, price_unit,ed_total):        
#        res = {}
#        subtotal_dep = 0
#        
#        if price_unit and ed_total:
#              subtotal_dep = price_unit
#              
#              res['price_subtotal'] = subtotal_dep
#              
#        return {'value':res}
    
    def create(self, cr, uid, vals, context=None):
        return super(sale_order_line, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids,vals,context=None):
        return super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
sale_order_line()

