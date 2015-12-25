from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp import pooler
from openerp.addons.Edumedia_India import config
import os
import openerp.tools
from openerp import netsvc

class ed_wiz_mailing_list(osv.osv_memory):
    _name='ed.wiz.mailing.list'
    _description='wizard class for mailing list'
    _columns={
              'category_id': fields.many2one('res.partner.category','Categories'), 
              'country_id':fields.many2one('res.country','Country'),
              'state_id':fields.many2one('res.country.state','State'),
              'ed_city_id': fields.many2one('ed.city', 'City'),
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
        } 
    _defaults ={
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
        for case in self.browse(cr,uid,ids):
            
            sqlstr = ""
            category = country = state = city = 0
            
            if case.category_id:
               category = case.category_id.id
           
            if case.country_id:
               country = case.country_id.id
            
            if case.state_id:
               state = case.state_id.id              
               
            if case.ed_city_id:
               city = case.ed_city_id.id
               
               
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.mailing.list' 
                 """)
              
                                       
            cr.execute("""  CREATE OR REPLACE VIEW ed_vw_mailing_list AS
                                SELECT 1 as id
                                      ,  """ + str(category) + """ as category_id
                                      ,  """ + str(country) + """ as country_id
                                      ,  """ + str(state) + """ as state_id
                                      ,  """ + str(city) + """ as ed_city_id;


                    """)
                                        
            cr.execute("""   CREATE OR REPLACE VIEW ed_vw_mailing_list_ln AS                                   
                                    select  q.id
                                          , q.partner_id 
                                          , q.address_id     
                                          , q.category 
                                          , 1 as main
                                            from 
                                            (select * from ed_mail_func(""" + str(category) + """,""" + str(country) + """
                                                                        ,""" + str(state) + """ ,""" + str(city) + """)
                                            )q;  

                    """)

                               
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.mailing.list')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.mailing.list' 
            return {
                'report_name': 'ed.vw.mailing.list', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }
ed_wiz_mailing_list()


class ed_wiz_training_list(osv.osv_memory):
    _name='ed.wiz.training.list'
    _description='Edumedia-India- Training list Report'
    _columns={
              'category_id': fields.many2one('res.partner.category','Categories'),
              'sch_date':fields.date('Schedule Date'),
              'user_id':fields.many2one('res.users','Assigned To'),
              'ed_complt':fields.selection([('no','NO'),('yes','Yes')],'Completed?'),
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
        }
    _defaults ={
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
        for case in self.browse(cr,uid,ids):
            
            sqlstr = completed = schdate = ""
            category = user = 0
            
            if case.category_id:
               category = case.category_id.id
                                   
            if case.sch_date:
                schdate = case.sch_date
                
            if case.user_id:
               user = case.user_id.id
               
               
            if case.ed_complt:
               completed = case.ed_complt
              
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.training.list' 
                 """)
                                       
            cr.execute("""  CREATE OR REPLACE VIEW ed_vw_training_list AS
                                SELECT 1 as id
                                      ,  """ + str(category) + """ as category_id
                                      ,  '""" + str(schdate) + """' as sch_date
                                      ,  """ + str(user) + """ as user_id
                                      ,  '""" + str(completed) + """' as ed_complt;
                      """)
                                        
            sqlstr = ("""   CREATE OR REPLACE VIEW ed_vw_training_list_ln AS                                   
                                    select   t.id
                                           , t.sale_id
                                           , t.partner_id
                                           , t.tname as name
                                           , t.schdate as sch_date
                                           , t.userid as user_id 
                                           , t.ed_stat
                                           , t.ed_complt
                                           , t.complt_on
                                           , t.category
                                           , 1 as main 
                                    from 
                                    ( select * from ed_training_func(""" + str(category) + """
                                                                    ,'""" + str(schdate) + """'
                                                                    ,""" + str(user) + """
                                                                    ,'""" + str(completed) + """'))t; 
                                    """)
                               
            

            cr.execute(sqlstr)
                               
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.training.list')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.training.list' 
            return {
                'report_name': 'ed.vw.training.list', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }

ed_wiz_training_list()  

class ed_wiz_payment_list(osv.osv_memory):
    _name='ed.wiz.payment.list'
    _description='Edumedia-India-Payment list Report'
    _columns={
              'category_id': fields.many2one('res.partner.category','Categories'),
              'nxt_payment_date' : fields.date('Next Payment Date'),
            'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
        }
    _defaults ={
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
        for case in self.browse(cr,uid,ids):
            
            sqlstr = nxtdate = ""
            category = 0
            
            if case.category_id:
               category = case.category_id.id
               
            if case.nxt_payment_date:
                nxtdate = case.nxt_payment_date
                                 
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.payment.list' 
                 """)
                                                  
            cr.execute("""  CREATE OR REPLACE VIEW ed_vw_payment_list AS
                                SELECT 1 as id
                                      ,  """ + str(category) + """ as category_id 
                                      ,  '""" + str(nxtdate) + """' as nxt_payment_date;
                      """)
                                        
            sqlstr = ("""   CREATE OR REPLACE VIEW ed_vw_payment_list_ln AS                                   
                                select  q.id 
                                      , q.sale_id 
                                      , q.partner_id
                                      , q.pay_amt as ed_amt
                                      , q.category as category
                                      , 1 as main 
                                from (select * from ed_payment_func(""" + str(category) + """
                                                                   ,'""" + str(nxtdate) + """'))q;
                        
                     """)
                               
            

            cr.execute(sqlstr)
                               
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.payment.list')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.payment.list' 
            return {
                'report_name': 'ed.vw.payment.list', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }

ed_wiz_payment_list()  


class ed_wiz_sessions_list(osv.osv_memory):
    _name='ed.wiz.sessions.list'
    _description='Edumedia-India- Sessions Report'
    _columns={
              'category_id':fields.many2one('res.partner.category','Categories'),
              'class_ids':fields.many2many('ed.vw.module','session_module_rel','session_id','module_id'),
            'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
            }
    _defaults ={
                'jasper_output':'pdf',
                }
        
    def print_report(self, cr, uid, ids, context=None): 
        
        for case in self.browse(cr,uid,ids):
            
            sqlstr = ""
            category = 0
            tids = clsids = ''
            if case.category_id:
               category = case.category_id.id
               
            if case.class_ids:         
                for t in case.class_ids:
                    tids += str(t.name) + ',' 
                clsids = tids[0:len(tids)-1]
                print clsids
                
            else:
                 clsids= '1,2,3,4,5,6,7,8'

                 print clsids
                                 
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.sessions.list' 
                 """)
                                                  
            cr.execute("""  CREATE OR REPLACE VIEW ed_vw_sessions_list AS
                                SELECT 1 as id
                                      ,  """ + str(category) + """ as category_id ;
                      """)
                                        
            sqlstr = ("""   CREATE OR REPLACE VIEW ed_vw_sessions_list_ln AS                                   
                                select  q.id
                                      , q.ed_school
                                      , q.sale_id 
                                      , q.module1
                                      , q.module2
                                      , q.module3
                                      , q.module4
                                      , q.module5
                                      , q.module6
                                      , q.module7
                                      , q.module8
                                      , q.parents
                                      , q.teachers
                                      , q.category
                                      , 1 as main 
                                from (select * from ed_session_func(""" + str(category) + """
                                                                    ,array[""" +str(clsids)+"""]))q;
                        
                     """)
                               
            

            cr.execute(sqlstr)
                               
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.sessions.list')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.sessions.list' 
            return {
                'report_name': 'ed.vw.sessions.list', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }

ed_wiz_sessions_list()

class ed_wiz_monthly_sessions(osv.osv_memory):
    _name='ed.wiz.monthly.sessions'
    _description ='Edumedia-India- Activity Sessions Report'
    _columns={
              'partner_id':fields.many2one('res.partner','School Name'),
              'date1':fields.date('From'),
              'date2':fields.date('To'),
              'ed_type' : fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Skills'),
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    _defaults ={
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
        for case in self.browse(cr,uid,ids):
            
            d_from = d_to = ""
           
            
            if case.date1:
                d_from = case.date1

            if case.date2:
                d_to = case.date2
                                                 
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.sessions.list' 
                 """)
            cr.execute("""CREATE OR REPLACE VIEW ed_vw_monthly_sessions AS
                                               SELECT   1 as id
                                                      ,""" + str(case.partner_id.id) +""" AS partner_id
                                                      ,'"""+ str(d_from) +"""' AS date1
                                                      ,'"""+ str(d_to) +"""' as date2
                                                      ,'"""+ str(case.ed_type) + """' as ed_type ;""")
            
            cr.execute("""CREATE OR REPLACE VIEW ed_vw_monthly_sessions_ln AS
                                                 select act.id
                                                       ,act.id as session_id  
                                                       ,array_to_string(array(select distinct emu.name 
                                                                              from ed_activity_session eas 
                                                                              inner join method_sessions_rel ms on ms.method_id = eas.id
                                                                              inner join ed_method_used emu on emu.id = ms.session_id 
                                                                              where eas.id = act.id),',') as other_actv
                                                       ,(select name from res_partner_address where partner_id = """ + str(case.partner_id.id) + """ and type = 'default') as cont_name
                                                       ,(select id from ed_sponsors 
                                                         where ed_skills = '"""+ str(case.ed_type) + """'
                                                         and scity_id = (select ed_city_id 
                                                                         from res_partner_address 
                                                                         where partner_id = """ + str(case.partner_id.id) +""" order by id limit 1)) as sponser_id
                                                       ,1 as main
                                                from ed_activity_session act 
                                                where act.ed_type = '"""+ str(case.ed_type) + """' and act.partner_id = """ + str(case.partner_id.id) + """
                                                and     act.ed_date between '"""+ str(d_from) +"""' 
                                                and '"""+ str(d_to) +""""'
                                                order by act.ed_date ASC;""")
                                                
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.monthly.sessions')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.monthly.sessions' 
            return {
                'report_name': 'ed.vw.monthly.sessions', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }                                            
    
ed_wiz_monthly_sessions()

class ed_wiz_time_table_list(osv.osv_memory):
    _name='ed.wiz.time.table.list'
    _description ='Edumedia-India- Time Table Report'
    #_auto=False
    _columns={ 'account_id':fields.many2one('account.fiscalyear','financial Year'),
               'city_id':fields.many2one('ed.city','City'),
               'name':fields.selection((['m1','JANUARY']
                                        ,['m2','FEBRUARY']
                                        ,['m3','MARCH']
                                        ,['m4','APRIL']
                                        ,['m5','MAY']
                                        ,['m6','JUNE']
                                        ,['m7','JULY']
                                        ,['m8','AUGUST']
                                        ,['m9','SEPTEMBER']
                                        ,['m10','OCTOBER']
                                        ,['m11','NOVEMBER']
                                        ,['m12','DECEMBER']),'MONTH'),
               'ed_type' : fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Skills'),
               'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    _defaults ={
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
        for case in self.browse(cr,uid,ids):
            
            mon = sqlstr = ""
            account = 0
            
            if case.account_id:
               account = case.account_id.id
            
            
            if case.name:
                mon = case.name
                sqlstr += """ and am.name = '""" +  str(mon) +"""'"""
                                                 
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.sessions.list' 
                 """)
    
            cr.execute(""" CREATE OR REPLACE VIEW ed_vw_time_table_list AS
                                SELECT 1 as id
                                      ,""" + str(account) + """  as account_id
                                      ,'""" + str(mon) + """ ' as name
                                      ,""" + str(case.city_id.id) + """ as city_id
                                      ,'""" + str(case.ed_type) + """' as ed_type ;""")
            
            cr.execute(""" CREATE OR REPLACE VIEW ed_vw_time_table_list_ln AS                                      
                                     select tl.id as id
                                           ,t.id as table_id
                                           ,tl.id as table_ln_id
                                           ,am.id as month_id
                                           ,1 as main
                                                     from 
                                                time_table t 
                                                inner join account_fiscalyear a on t.account_id = a.id 
                                                inner join ed_auto_month am on am.table_id = t.id 
                                                inner join time_table_lines tl on tl.month_id = am.id
                                                where tl.ed_type = '""" + str(case.ed_type) + """' and t.account_id = """ + str(account) + """ 
                                                and t.city_id = """ + str(case.city_id.id) + """
                                                """ + str(sqlstr) +"""
                                                order by am.name,tl.day_id ASC ; """)
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.time.table.list')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.time.table.list' 
            
            return {
                'report_name': 'ed.vw.time.table.list', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }
    
ed_wiz_time_table_list()


class ed_wiz_topic_list(osv.osv_memory):
    _name='ed.wiz.topic.list'
    _description ='Edumedia-India- List of Topic  Report'
    _columns={
              'start_date':fields.date('Start Date'),
              'end_date':fields.date('End Date'),
              'is_5': fields.boolean('5th Std'),
              'is_6': fields.boolean('6th Std'),
              'is_7': fields.boolean('7th Std'),
              'is_8': fields.boolean('8th Std'),
              'is_9': fields.boolean('9th Std'),
              'is_10': fields.boolean('10th Std'),
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    _defaults ={  
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
       for case in self.browse(cr,uid,ids):
         clsids = []
         if case.is_5: clsids.append(5)
         if case.is_6: clsids.append(6)
         if case.is_7: clsids.append(7)
         if case.is_8: clsids.append(8)
         if case.is_9: clsids.append(9)
         if case.is_10: clsids.append(10)
         
         if not clsids or len(clsids) == 0:
             clsids = [5,6,7,8,9,10]
              
         cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'fp.vw.tds.rpt' 
                 """) 
            
         cr.execute(""" CREATE OR REPLACE VIEW ed_vw_topic_list AS
                                select 1 as id
                                      ,'""" + str(case.start_date) + """' as start_date    
                                      ,'""" + str(case.end_date) + """' as end_date;""")
         
         
         cr.execute("""CREATE OR REPLACE VIEW ed_vw_topic_list_ln AS
                                   SELECT   q.id
                                           ,q.tot_sessions
                                           ,q.tot_sessions1
                                           ,q.school_id as partner_id
                                           ,q.ed_class
                                           ,q.status
                                           ,q.topic
                                           ,1 as main
                                   FROM (select * from func_topic('""" + str(case.start_date) + """'
                                                               , '""" + str(case.end_date) + """'
                                                               , array""" + str(clsids) + """)
                                                       order by id ASC)q;
                    """)
         
         res = []
         main_obj = pooler.get_pool(cr.dbname).get('ed.vw.topic.list')
         res = main_obj.search(cr, uid, []) 
         data = {}
         data['ids'] = res 
         data['model'] = 'ed.vw.topic.list' 
          
         return {
                'report_name': 'ed.vw.topic.list', 
                'type': 'ir.actions.report.xml',            
                'target': 'new',
                'datas': data,
                }
    
ed_wiz_topic_list()

class ed_wiz_career(osv.osv_memory):
    _name='ed.wiz.career'
    _description ='Edumedia-India- Career graph  Report'
    _columns={
            
              'department_id':fields.many2one('hr.department','Department'),

              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    _defaults ={  
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
       for case in self.browse(cr,uid,ids):
            
            department = 0
            
            if case.department_id:
               department = case.department_id.id
            

            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'vw.ed.career' 
                 """) 
            
            cr.execute(""" CREATE OR REPLACE VIEW vw_ed_career AS
                                select 1 as id
                                      ,""" + str(department) + """ as department_id;
                        """)
         
            cr.execute("""CREATE OR REPLACE VIEW vw_ed_career_lines AS
                                select q.id
                                      , q.employee_id
                                      , q.contract_id
                                      , q.date_of_join
                                      , q.ac_conform_due_date
                                      , q.leave_date
                                      , q.date_start
                                      , q.date_end
                                      , 1 as main
                                from 
                                ( select * from ed_career_func(""" + str(department) + """))q;
                        """)
         
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('vw.ed.career')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'vw.ed.career' 
          
            return {
                    'report_name': 'vw.ed.career', 
                    'type': 'ir.actions.report.xml',            
                    'target': 'new',
                    'datas': data,
                   }
    
ed_wiz_career()


class ed_wiz_allocation(osv.osv_memory):
    _name='ed.wiz.allocation'
    _description ='Edumedia-India- Allocation  Report'
    _columns={ 
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    _defaults ={  
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
       for case in self.browse(cr,uid,ids):
             

            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'vw.ed.allocation' 
                 """) 
            
            cr.execute(""" CREATE OR REPLACE VIEW vw_ed_allocation AS
                                select 1 as id;
                       """)
         
            cr.execute(""" CREATE OR REPLACE VIEW vw_ed_allocation_lines AS
                            select t.id
                                  , t.department_id
                                  , t.job_id
                                  , t.name
                                  ,1 as main
                            from 
                            ( select * from ed_allocation())t;
                        """)           
         
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('vw.ed.allocation')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'vw.ed.allocation' 
          
            return {
                    'report_name': 'vw.ed.allocation', 
                    'type': 'ir.actions.report.xml',            
                    'target': 'new',
                    'datas': data,
                   }
    
ed_wiz_allocation()

class ed_wz_stock_rpt(osv.osv_memory):
    _name = 'ed.wz.stock.rpt' 
    _description = "Edumedia - Stock Report Wizard"
    
    _columns = {   
             'name'  : fields.many2one('product.product', 'Component/Product'), 
             'start_dt' : fields.date('Start Date'), 
             'end_dt' : fields.date('End Date'), 
             'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
                } 
    _defaults = {
                 'jasper_output':'pdf',
                 }
    
    def print_report(self, cr, uid, ids, *args):
        
        for case in self.browse(cr,uid,ids):
            prod_obj = self.pool.get('product.product')
            
            if case.name:
               prod_ids = prod_obj.search(cr,uid,[('id','=',case.name.id)])
            else :
               prod_ids = prod_obj.search(cr,uid,[]) 
               
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                           where model = 'ed.view.stock.rpt1' 
                   """)
                    
            if case.end_dt < case.start_dt:
                 raise osv.except_osv(_('UserError'), _('Please Check the Dates!!')) 
            cr.execute(""" CREATE OR REPLACE VIEW ed_view_stock_rpt1 AS
                            SELECT 1 as id 
                                 , """ + str(case.name and case.name.id or 0 )+""" as name
                                 , '""" + str(case.start_dt) + """' as start_dt
                                 , '""" + str(case.end_dt) + """' as end_dt;
 
                        """) 

            cr.execute(""" SELECT ed_stock_detail (""" + str(uid) + """,array""" + str(prod_ids)+"""
                                                     , '""" + str(case.start_dt) + """', '""" + str(case.end_dt) + """');
                        """)
            
            cr.execute(""" CREATE OR REPLACE VIEW ed_view_stock_rpt_lines AS
                             SELECT t.id
                                  , t.stk_dt
                                  , t.seq 
                                  , t.product_id
                                  , t.detail
                                  , t.reference
                                  , t.opening 
                                  , t.arrival
                                  , t.issue 
                                  , t.closing
                                  , 1 as main
                              FROM tmp_stock_detail t
                              WHERE t.uid = """ + str(uid) + """
                              AND t.id not in (select id from   tmp_stock_detail 
                                               where (opening = 0 and arrival = 0 
                                               and issue = 0 and closing = 0));
                        """)
        
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.view.stock.rpt1')
            res = main_obj.search(cr, uid, [])
        
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.view.stock.rpt1' 
            return {
                'report_name': 'ed.view.stock.rpt1',
                'type': 'ir.actions.report.xml',
                'target': 'new',
                'datas': data,
                }  
    
ed_wz_stock_rpt()

class ed_wiz_appraisal_score(osv.osv_memory):
    _name='ed.wiz.appraisal.score'
    _description ='Edumedia-India- Appraisal Score'
    _columns={'resource_id' : fields.many2one('ed.resource.appraisal','Resource Appraisal',required=True),
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    _defaults ={  
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
       for case in self.browse(cr,uid,ids):

            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.appraisal.score' 
                 """) 
            
            cr.execute(""" CREATE OR REPLACE VIEW ed_vw_appraisal_score AS
                                select 1 as id
                                      ,""" + str(case.resource_id.id) + """ as resource_id;
                        """)
         
            cr.execute("""CREATE OR REPLACE VIEW ed_vw_appraisal_score_ln AS
                               select   eo.id
                                       ,eo.id as summary_id 
                                       ,1 as main
                               from ed_appraisal ea 
                               inner join ed_app_overall eo on eo.appraisal_id = ea.id
                               where ea.resource_id=""" + str(case.resource_id.id) + """ 
                               order by id;
                        """)
         
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('vw.ed.career')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.appraisal.score' 
          
            return {
                    'report_name': 'ed.vw.appraisal.score', 
                    'type': 'ir.actions.report.xml',            
                    'target': 'new',
                    'datas': data,
                   }
    
ed_wiz_appraisal_score()

class ed_wiz_erp_implemantation(osv.osv_memory):
    
    _name = 'ed.wiz.erp.implemantation'
    _description = 'Edumedia-India - ERP-Implementation'
    _columns={
              'start_dt' : fields.date('Start Date'), 
              'end_dt'   : fields.date('End Date'),
              'city_id'  : fields.many2one('ed.city','City'),
              'user_id'  : fields.many2one('res.users','Eduvisor'),
              'jasper_output': fields.selection([('pdf','PDF'),('xls','XLS')], 'Report Output'),
              }
    
    _defaults ={  
                'jasper_output':'pdf',
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        
       for case in self.browse(cr,uid,ids):
            sqlstr = ""
            if case.end_dt < case.start_dt:
                 raise osv.except_osv(_('UserError'), _('Please Check the Dates!!')) 
             
            if case.city_id:
                sqlstr += """ and rpa.ed_city_id = """ + str(case.city_id.id)
                
            if case.user_id:
                sqlstr += """ and so.user_id = """ + str(case.user_id.id)
            
            cr.execute(""" update ir_act_report_xml set jasper_output = '""" + case.jasper_output + """' 
                            where model = 'ed.vw.appraisal.score' 
                 """) 
            
            cr.execute(""" CREATE OR REPLACE VIEW ed_vw_erp_implemantation AS
                                select 1 as id
                                      ,'""" + str(case.start_dt) + """ ' as start_dt
                                      ,'""" + str(case.end_dt) + """' as end_dt
                                      ,""" + str(case.city_id and case.city_id.id or 0) + """ as city_id
                                      ,""" + str(case.user_id and case.user_id.id or 0)+""" as user_id;
                        """)
         
            cr.execute("""CREATE OR REPLACE VIEW ed_vw_erp_implemantation_ln AS                                         
                                    select   distinct(so.id)
                                            ,so.id as sale_id
                                            ,so.name as so_name
                                            ,(select sp.id from product_category pc
                                                           inner join product_template pt on pt.categ_id = pc.id 
                                                           inner join stock_move sm on sm.product_id = pt.id
                                                           inner join stock_picking sp on sp.id = sm.picking_id
                                                           where sp.sale_id = so.id and sp.state = 'done' 
                                                           and pc.name ='HDD'limit 1) as cdd_id
                                            ,(select sp.id from product_category pc
                                                        inner join product_template pt on pt.categ_id = pc.id 
                                                        inner join stock_move sm on sm.product_id = pt.id
                                                        inner join stock_picking sp on sp.id = sm.picking_id
                                                        where sp.sale_id = so.id and sp.state = 'done' 
                                                        and pc.name='Products (SC)' limit 1) as workbk_id 
                                            ,case when (select count(id) from sale_order where partner_id = so.partner_id and state != 'draft') > 1 then 'Existing' else 'New' end as scl_exist
                                            ,(select sum(ed_students)from ed_class_details where sale_id = so.id) as tot_stu
                                            ,(select sum(price_unit) from sale_order_line where order_id = so.id and lower(name)!= 'license') as price_unit
                                            , 1 as main
                                    from sale_order so 
                                    inner join res_partner_address rpa on rpa.id = so.partner_order_id
                                    where so.date_order between '""" + str(case.start_dt) + """' and '""" + str(case.end_dt) + """'
                                    and so.state not in ('draft','cancel')
                                    """ + str(sqlstr) + """
                                    order by so.id;
                        """) 
         
            res = []
            main_obj = pooler.get_pool(cr.dbname).get('ed.vw.erp.implemantation')
            res = main_obj.search(cr, uid, []) 
            data = {}
            data['ids'] = res 
            data['model'] = 'ed.vw.erp.implemantation' 
          
            return {
                    'report_name': 'ed.vw.erp.implemantation', 
                    'type': 'ir.actions.report.xml',            
                    'target': 'new',
                    'datas': data,
                   }    
    
ed_wiz_erp_implemantation()

