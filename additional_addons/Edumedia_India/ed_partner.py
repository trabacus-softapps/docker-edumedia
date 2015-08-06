from openerp.osv import fields,osv
from openerp.tools.translate import _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
class res_partner(osv.osv): 
    _inherit = 'res.partner'
      
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        context = dict(context or {})
        sup_id = cust_id = mentor = 0  
        
        tree_name = 'ed_partner_tree'
        search_name = 'ed.res.partner.select' 
        form_name = 'view_ed_partner_form'  
            
        if 'search_default_supplier' in context:
            sup_id = context.get('search_default_supplier',False)
            
        if 'mentor' in context:
            mentor = context.get('mentor',False)
        
        if 'search_default_customer' in context:
            cust_id=context.get('search_default_customer',False)
            
        if sup_id:
            tree_name = 'res.partner.tree'
            search_name = 'res.partner.select'
            form_name = 'res.partner.form'
            
        if cust_id:
            tree_name = 'ed_partner_tree'
            search_name = 'ed.res.partner.select'
            form_name = 'view_ed_partner_form'
            
        if mentor:
            tree_name = 'ed_partner_mentor_tree'
            search_name = 'ed_view_res_partner_mentor_filter'
            form_name = 'view_ed_mentor_partner_form'
    
        if not view_type:
           view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', tree_name)])
           view_type = 'tree'
             
        if view_type == 'tree':
           view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', tree_name)])   
             
        if view_type == 'search':
           view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', search_name)])   
             
        if view_type == 'form':
           view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', form_name)])
             
        if view_id and isinstance(view_id, (list, tuple)):
           view_id = view_id[0] 
        return super(res_partner,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        
             
    def _get_sale_ids(self, cr, uid, ids, field_name, arg, context=None):
        
        sale_obj = self.pool.get("sale.order")
        res = {}
        for case in self.browse(cr,uid,ids,context):
            res[case.id] = sale_obj.search(cr, uid, [('partner_id', '=', case.id)])
            
        return res
    
    def _get_session_ids(self, cr, uid, ids, field_name, arg, context=None):
        
        sale_obj = self.pool.get("ed.activity.session")
        res = {}
        for case in self.browse(cr,uid,ids,context):
            res[case.id] = sale_obj.search(cr, uid, [('partner_id', '=', case.id)])
            
        return res
    
#    def _get_subscrip(self,cr,uid, ids, name, args, context=None):
#        
#        res={}
#        for case in self.browse(cr,uid,ids):
#            res[case.id] = False          
#            cr.execute("select id from ed_subscription where now() between start_date and end_date and state='confirmed' and partner_id = %d order by id desc limit 1 " %(case.id))
#            subscription =cr.fetchone() 
#            if subscription and subscription[0]: 
#                res[case.id] = True         
#        return res

                 
    _columns={
                
                'ed_sh_complem' : fields.boolean('Complementary'),
                'ed_sh_subscrip' : fields.boolean ('Subscription',readonly=True),
                'ed_sh_cinema':fields.boolean('School Cinema',readonly=False), 
                'ed_sh_kr':fields.boolean('Krayon'),
                'ed_sh_men':fields.boolean('Mentor'), 
                'ed_sh_act':fields.boolean('Activity'), 
                'ed_sh_aksh':fields.boolean('Akshaya'),
                'ed_total_strg':fields.integer('Total Strength'),
                'ed_grade_off':fields.char('Grades Offered',size=100),
                'ed_co_ed':fields.boolean('Co Education'),
                'ed_board_id':fields.many2one('ed.board','Board',size=100),
                'ed_event_ids':fields.one2many('ed.events','partner_id','Event'),
                'ed_infra_ids':fields.many2many('ed.infrastucture','ed_partner_ifra_rel','partner_id','infra_id'),
                'ed_cls_ids':fields.one2many('ed.class.details','partner_id','Class'),
                'ed_moral_ids':fields.many2many('ed.moral.edu','ed_partner_moral_rel','partner_id','moral_id'),
                'ed_ser_tax_no' : fields.char('Service Tax No',size=50),
                'ed_pan_no' : fields.char('PAN',size=50),
                'ed_vat_no' : fields.char('VAT  Reg No',size=50),
                'ed_state':fields.boolean('State'),
                'ed_cin':fields.char('CIN',size=50),
                'ed_tin':fields.char('TIN NO.',size=50),
                'ed_text':fields.text('Notes'),
                'type' : fields.many2one('ed.type','Type'),
                'ed_city_id': fields.related('child_ids', 'ed_city_id', type='many2one', relation='ed.city', string='City'),
                'sale_ids': fields.function(_get_sale_ids, method=True, type='one2many', obj='sale.order', string='Sale Orders' ,readonly=True),
#                 'time_from':fields.time('From'),
#                 'time_to':fields.time('To'),
                'time_from':fields.datetime('From'),
                'time_to':fields.datetime('To'),
                'ed_session_ids': fields.function(_get_session_ids, method=True, type='one2many', obj='ed.activity.session', string='Sessions' ,readonly=True),
                'ed_cont_name': fields.related('child_ids', 'name', type='char',size=500, string='Contact Name'),
                'ed_street_id': fields.related('child_ids', 'street', type='char',size=500, string='Street'),
                'ed_street2_id': fields.related('child_ids', 'street2', type='char',size=500, string='Street2'),
                'ed_mobile': fields.related('child_ids', 'mobile', type='char',size=500, string='Mobile'),
                'ed_source': fields.selection([('dir_con', 'Director Contact'),('event', 'Event'),('sch_cin', 'School Cinema'),('men_conclv', 'Mentor Conclave'),('conf', 'Conference')], 'Source'),
                
                'ed_desig_id':fields.many2one('ed.designation','Designation'),
                'ed_birth':fields.date('Birthday'),
                #'ed_city_id':fields.many2one('ed.city','City', select=True),
                'sch_email' : fields.char('School Email',size=50),
                'sch_phone' : fields.integer('School Phone',size=20),
   } 
    _defaults={
              'ed_sh_complem' :False,
              'ed_sh_subscrip' :False,
               }
     
     
   
#    def mark_Subscription(self, cr, uid, ids, context=None):
#    def mark_Subscription(self, cr, uid, automatic=False, use_new_cursor=False, context=None):        
#        subcrip_obj = self.pool.get('ed.subscription')
#        subscrp_ids = False
#        cr.execute("select id from ed_subscription where state='confirmed'")
#        subscrp_ids = cr.fetchall() 
#        today = time.strftime('%Y-%m-%d')
#        for s in subscrp_ids:
#           for subs in subcrip_obj.browse(cr,uid,[s[0]]):
#               if today > subs.end_date:
#                    subcrip_obj.write(cr,uid,[subs.id],{'state':'closed'}) 
#                    if subs.partner_id:
#                       self.write(cr,uid,[subs.partner_id.id],{})     
#        return True
       
    def create(self, cr, uid, vals, context=None):
        context = dict(context or {})
        partner_id = False
        class_obj = self.pool.get('ed.class.details')          
        vals.update({'ed_state': True})
        res_id=super(res_partner, self).create(cr, uid, vals, context)
        context.update({'partner_id':res_id})
        for i in range(1,11):
            class_obj.create(cr,uid,{'partner_id' : res_id,
                             'ed_class' : i,
                             'ed_boys':0,
                             'ed_girls':0,
                             'ed_sec':0,
                             'ed_students':0},context) 
        return res_id
           
           
#    def write(self, cr, uid, ids,vals,context=None): 
#        sale_obj = self.pool.get('sale.order') 
#        
#        result = super(res_partner, self).write(cr, uid, ids, vals, context=context)
#        
#        case = self.browse(cr, uid, id)
#        part_cls_ids = set()         
#        if case.ed_cls_ids:
#            for c in case.ed_cls_ids:
#                if c.ed_class not in (9,10):
#                    part_cls_ids.add(c.id) 
#        cr.execute("select id from sale_order where partner_id = %d"%(case.id))
#        sale_ids = cr.fetchall()
#        if sale_ids:
#            for si in sale_ids:  
#                for s in sale_obj.browse(cr, uid, [si[0]]):
#                    sale_cls_ids = new_cls_ids = set()
#                    if s.class_ids:             
#                        for c in s.class_ids:
#                            sale_cls_ids.add(c.id)
#                        new_cls_ids = part_cls_ids - sale_cls_ids 
#                        for n in new_cls_ids:
#                            cr.execute("insert into class_sale_rel(sale_id, cls_id) values(%d,%d)"%(s.id, n))
#                                   
#        return result
      
res_partner()    

# class res_partner_address(osv.osv): 
#       _inherit = 'res.partner.address'
#       _columns={ 
#                 
#                 'ed_desig_id':fields.many2one('ed.designation','Designation'),
#                 'ed_birth':fields.date('Birthday'),
#                 'ed_city_id':fields.many2one('ed.city','City', select=True),
#                 'sch_email' : fields.char('School Email',size=50),
#                 'sch_phone' : fields.integer('School Phone',size=20),
#                 }
#       
# res_partner_address()

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
#                'user_count':fields.integer('User Count'),
                'sponsor_ids' : fields.one2many('ed.sponsors','comp_id','Sponsors'),
               }
res_company()

class res_users(osv.osv):
    _inherit='res.users'
    
    def _get_city_id(self, cr, uid, ids, field_name, arg, context=None):
        
        hr_obj = self.pool.get("hr.employee")
        resource_obj = self.pool.get('resource.resource')
        res = {}
        for case in self.browse(cr,uid,ids,context):
            res[case.id] = False
            hr_id = False
            resource_id = resource_obj.search(cr, uid, [('user_id', '=',case.id)],limit=1)
            if resource_id:
                hr_id = hr_obj.search(cr,uid,[('resource_id','=',resource_id[0])],limit=1)
            if hr_id :
                hr_emp = hr_obj.browse(cr,uid,hr_id[0])
                res[case.id] = hr_emp.address_id.ed_city_id.id
        return res
    
    _columns={
              'city_id':fields.many2one('ed.city','City'),
#              for holiday dashboard purpose
              'wrkcity_id':fields.function(_get_city_id, method=True, type='many2one', obj='ed.city', string='Employee Address City',readonly=True, store=True),
              }
    
#    def create(self, cr, uid, vals, context=None):
#        user_id = 0
#        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
#        cr.execute('select count(id) from res_users')
#        count = cr.fetchone()
#        if count and count[0] < company.user_count :
#            user_id = super(res_users, self).create(cr, uid, vals, context)
#            return user_id
#        
#        else :
#            raise osv.except_osv(_('Warning'),_("Cannot Create User ...... Limit Exceeded"))  
    
res_users()
       