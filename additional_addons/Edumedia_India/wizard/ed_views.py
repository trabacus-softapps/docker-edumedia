from openerp.osv import fields,osv
from openerp.tools.translate import _ 
import openerp.tools.sql
from openerp.addons.Edumedia_India import config
from openerp import tools

class vw_res_partner_address(osv.osv):  
    _name = 'vw.res.partner.address'
    _description = 'view Partner address'
    _auto = False  
    _columns = {
               'name':fields.char('Name',size=50,required=False,store=True),
               'mobile': fields.integer('Mobile'),
               'email':fields.char('Email', size=240),
               'ed_desig_id':fields.many2one('ed.designation','Designation'),
               'sale_id':fields.many2one('sale.order','sale id'),
        }    
    
vw_res_partner_address()

class vw_res_partner(osv.osv): 
    _name = 'vw.res.partner'
    _description = 'view Partner'
    _auto = False 
    _columns = {
               'partner_id':fields.many2one('res.partner','Partner'),
               'stock_id':fields.many2one('stock.picking','Picking'),
               'sale_id':fields.many2one('sale.order','sale id'),
        }    
    
vw_res_partner()

class vw_ed_subscription(osv.osv): 
    _name = 'vw.ed.subscription'
    _description = 'view Subscription'
    _auto = False 
    _columns = {
               'subscrib_id':fields.many2one('ed.subscription','Subscription'),
               'monthly_id':fields.many2one('ed.monthly.edition','Edition'),
        }    
    
vw_ed_subscription()

class vw_ed_advertisers(osv.osv): 
    _name = 'vw.ed.advertisers'
    _description = 'view Advertisers'
    _auto = False 
    _columns = {
               'advertiser_id':fields.many2one('ed.advertisers.details','Advertisers'),
               'monthly_id':fields.many2one('ed.monthly.edition','Edition'),
        }    
    
vw_ed_advertisers()

class vw_ed_director(osv.osv): 
    _name = 'vw.ed.director'
    _description = 'view Director'
    _auto = False 
    _columns = {
               'director_id':fields.many2one('ed.director.details','Advertisers'),
               'monthly_id':fields.many2one('ed.monthly.edition','Edition'),
        }    
    
vw_ed_director()


class vw_ed_class_details(osv.osv):
    _name='vw.ed.class.details'
    _description = 'view class details'
    _auto = False 
    _columns={
              'ed_class':fields.integer('Class'),
              'ed_sec':fields.integer('No.Of.Sections'),
              'ed_students':fields.integer('No.Of.Students'),
              'ed_boys':fields.integer('NO.Of.Boys'),
              'ed_girls':fields.integer('NO.Of.Girls'),
              'girls':fields.integer('Girls'),
              'boys':fields.integer('Boys'),
              'sale_id':fields.many2one('sale.order','sale id')
             }
vw_ed_class_details() 

class ed_vw_mailing_list(osv.osv):
    _name='ed.vw.mailing.list'
    _description='Edumedia-India- Mailing List Report'
    _auto = False
    _columns={
              'category_id': fields.many2one('res.partner.category','Categories'),
              'country_id':fields.many2one('res.country','Country'),
              'state_id':fields.many2one('res.country.state','State'),
              'ed_city_id': fields.many2one('ed.city', 'City'),
              'lines' : fields.one2many('ed.vw.mailing.list.ln', 'main', 'Lines'),
              }
ed_vw_mailing_list()
 
class ed_vw_mailing_list_ln(osv.osv):
    _name='ed.vw.mailing.list.ln'
    _description='Edumedia-India- Mailing List Report'
    _auto = False
    _columns={
              'partner_id':fields.many2one('res.partner','Partner'),
              #'address_id':fields.many2one('res.partner.address','Address'),
              'address_id':fields.many2one('res.partner','Address'),
              'category':fields.char('Categories',size=200),              
              'main':fields.many2one('ed.vw.mailing.list','Main')
              }
    _order = 'partner_id'
    
ed_vw_mailing_list_ln()

class ed_vw_training_list(osv.osv):
    _name='ed.vw.training.list'
    _description='Edumedia-India- Training list Report'
    _auto= False
    _columns={
              'category_id': fields.many2one('res.partner.category','Categories'),
              'sch_date':fields.date('Schedule Date'),
              'user_id':fields.many2one('res.users','Assigned To'),
              'ed_complt':fields.selection([('no','NO'),('yes','Yes')],'Completed?'),
              'lines':fields.one2many('ed.vw.training.list.ln','main','Lines'),
              }

ed_vw_training_list()  

class ed_vw_training_list_ln(osv.osv):
    _name='ed.vw.training.list.ln'
    _description='Edumedia-India- Training list Report'
    _auto= False
    _columns={
               'sale_id': fields.many2one('sale.order','Sale Oder'),
               'partner_id':fields.many2one('res.partner','Partner'),
               'name':fields.char('Description',size=300),
               'sch_date':fields.date('Schedule Date'),
               'user_id':fields.many2one('res.users','Assigned To'),
               'ed_stat':fields.char('Status',size=300),
               'ed_complt':fields.char('Completed?',size=16),
               'complt_on':fields.date('Completed On'),
               'category':fields.text('Categories'),
               'main':fields.many2one('ed.vw.training.list','Main')
              }
    _order = 'partner_id,sale_id'
ed_vw_training_list_ln() 

class ed_vw_payment_list(osv.osv):
    _name='ed.vw.payment.list'
    _description ='Edumedia-India- Payment list Report'
    _auto=False
    _columns={
              'category_id': fields.many2one('res.partner.category','Categories'),
              'nxt_payment_date' : fields.date('Next Payment Date'),
              'lines':fields.one2many('ed.vw.payment.list.ln','main','Lines'),
              }
    
ed_vw_payment_list()

class ed_vw_payment_list_ln(osv.osv):
    _name='ed.vw.payment.list.ln'
    _description ='Edumedia-India- Payment list Report'
    _auto=False
    _columns={
              'sale_id': fields.many2one('sale.order','Sale Oder'),
              'partner_id':fields.many2one('res.partner','Partner'),
              'ed_amt':fields.float('Amount'),
              'category':fields.text('Categories'),
              'main':fields.many2one('ed.vw.payment.list','Main')
              }
ed_vw_payment_list_ln()

class ed_vw_sessions_list(osv.osv):
    _name='ed.vw.sessions.list'
    _description ='Edumedia-India- Sessions Report'
    _auto=False
    _columns={
              'category_id':fields.many2one('res.partner.category','Categories'),
              'lines':fields.one2many('ed.vw.sessions.list.ln','main','Lines'),
              }
    
ed_vw_sessions_list()


class ed_vw_sessions_list_ln(osv.osv):
    _name='ed.vw.sessions.list.ln'
    _description ='Edumedia-India- Sessions Report'
    _auto=False
    _columns={
              'ed_school':fields.char('School Name',size=100),
              'sale_id': fields.many2one('sale.order','Sale Oder'),
              'module1':fields.integer('Module1'),
              'module2':fields.integer('Module2'),
              'module3':fields.integer('Module3'),
              'module4':fields.integer('Module4'),
              'module5':fields.integer('Module5'),
              'module6':fields.integer('Module6'),
              'module7':fields.integer('Module7'),
              'module8':fields.integer('Module8'),
              'parents':fields.integer('Parents'),
              'teachers':fields.integer('Teachers'),
              'category':fields.text('Categories'),
              'main':fields.many2one('ed.vw.sessions.list','Main')
              }
    
ed_vw_sessions_list_ln()


class ed_vw_module(osv.osv):
    _name='ed.vw.module'
    _description ='Module/Class'
    #_auto=False 
    _columns={'name':fields.integer('Module')
              }
    
#    def init(self, cr):
#       
#       tools.sql.drop_view_if_exists(cr, 'ed_vw_module') 
#       cr.execute( """ 
#                            CREATE OR REPLACE VIEW ed_vw_module AS 
#                             SELECT a.id
#                                  , a.id as name
#                             FROM
#                             (    select unnest(array[1, 2, 3, 4, 5, 6, 7, 8]) as id
#                             )a;
#                """)


ed_vw_module()   
   
class ed_vw_monthly_sessions(osv.osv):
    _name='ed.vw.monthly.sessions'
    _description ='Edumedia-India- Activity Sessions Report'
    _auto=False
    _columns={
              'partner_id':fields.many2one('res.partner','School'),
              'date1':fields.date('From'),
              'date2':fields.date('To'),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              'lines':fields.one2many('ed.vw.monthly.sessions.ln','main','Lines'),
              }
    
ed_vw_monthly_sessions()


class ed_vw_monthly_sessions_ln(osv.osv):
    _name='ed.vw.monthly.sessions.ln'
    _description ='Edumedia-India- Activity Sessions Report Lines'
    _auto=False
    _columns={
              'session_id':fields.many2one('ed.activity.session','Monthly Session'),
              'other_actv':fields.text('Other Activities'), 
              'cont_name' :fields.char('Contact Name',size=64),
              'sponser_id':fields.many2one('ed.sponsors','Sponser'),
              'main':fields.many2one('ed.vw.monthly.sessions','Main')
              }
    
ed_vw_monthly_sessions_ln()

class ed_vw_time_table_list(osv.osv):
    _name='ed.vw.time.table.list'
    _description ='Edumedia-India- Time Table Report'
    _auto=False
    _columns={ 'account_id':fields.many2one('account.fiscalyear','financial Year'),
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
              'city_id':fields.many2one('ed.city','City'),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              'lines':fields.one2many('ed.vw.time.table.list.ln','main','Lines'),
              }
    
ed_vw_time_table_list()

class ed_vw_time_table_list_ln(osv.osv):
    _name='ed.vw.time.table.list.ln'
    _description ='Edumedia-India- Time Table Report Lines'
    _auto=False
    _columns={ 'table_id':fields.many2one('time.table','Time Table'),
               'table_ln_id':fields.many2one('time.table.lines','Time Table Lines'),
               'month_id':fields.many2one('ed.auto.month',"Month"),
              'main':fields.many2one('ed.vw.time.table.list','Main'),
              }
    _order = 'month_id' 
ed_vw_time_table_list_ln()

class ed_vw_topic_list(osv.osv):
    
    _name='ed.vw.topic.list'
    _description ='Edumedia-India- List Of Topics Report'
    _auto=False
    _columns={
               'start_date':fields.date('Start Date'),
               'end_date':fields.date('End Date'),
              'lines':fields.one2many('ed.vw.topic.list.ln','main','Lines'),
              }
ed_vw_topic_list()

class ed_vw_topic_list_ln(osv.osv):
    
    _name='ed.vw.topic.list.ln'
    _description ='Edumedia-India- List Of Topics Report lines'
    _auto=False
    _columns={'tot_sessions':fields.integer('Total Sessions'),
              'tot_sessions1':fields.integer('Total Sessions1'),
              'partner_id':fields.many2one('res.partner','Partner'),
              'ed_class':fields.integer('Class'),
              'status' :fields.char('Status',size=50),
              'topic':fields.text('Topic'),
               'main':fields.many2one('ed.vw.topic.list','Main'),
              }   
ed_vw_topic_list_ln()

class vw_ed_career(osv.osv):
    
    _name='vw.ed.career'
    _description ='Edumedia-India- Career Graph Report'
    _auto=False
    _columns={
               'department_id':fields.many2one('hr.department','Department'),
               'lines':fields.one2many('vw.ed.career.lines','main','Lines')
              }
vw_ed_career()

class vw_ed_career_lines(osv.osv):
    
    _name='vw.ed.career.lines'
    _description ='Edumedia-India- Career Graph Report lines'
    _auto=False
    _columns={
               'employee_id' : fields.many2one('hr.employee','Employee'),
               'contract_id' :fields.many2one('hr.contract','Contracts'),
               'date_of_join':fields.char('Date Of Join',size=15),
               'ac_conform_due_date':fields.char('Date Of Confirmation',size=15),
               'leave_date':fields.char('Date of Leaving',size=15),
               'date_start':fields.char('Salary Start Date',size=15),
               'date_end':fields.char('Salary End Date',size=15),
               'main':fields.many2one('vw.ed.career','Main')
              }
    _order = "employee_id,contract_id"   
vw_ed_career_lines()


class ed_vw_birthday(osv.osv):
    _name = 'ed.vw.birthday'
    _description = 'Edumedia- Birthday'
    _auto = False
    _columns = {
                'employee_id' : fields.many2one("hr.employee","Employee"),
                'birthday' : fields.char("Birthday",size=30),
                }
    _order = "birthday"
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ed_vw_birthday')
        print "a called"
        cr.execute(""" 
                    CREATE OR REPLACE VIEW ed_vw_birthday AS
                      select e.id 
                           , e.id as employee_id    
                           , to_char(e.birthday,'DD-MONTH') as birthday 
                      from hr_employee e
                      where (extract(year from now()) || '-' || extract(month from e.birthday) || '-' || extract(day from e.birthday)) :: date 
                      between now()::date and (now()::date + integer '10');
        """)
ed_vw_birthday()

class ed_vw_holidays(osv.osv):
    _name = 'ed.vw.holidays'
    _description = 'Edumedia- Holidays'
    _auto = False
    _columns = {
                'holiday' : fields.char("Holiday",size=30),
                'h_year' : fields.char("Year",size=5),
                'h_date' : fields.date('Day'),
                'city_id':fields.many2one('ed.city','City'),
                }
    _order = "h_date"
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ed_vw_holidays')
#        user_id = context and context.get('user_id',False)
        cr.execute(""" 
                    CREATE OR REPLACE VIEW ed_vw_holidays AS
                      select id,
                             name as holiday,
                             extract(year from h_date) as h_year,
                             h_date,
                             city_id
                      from ed_holiday 
                    ;""")
ed_vw_holidays()

class vw_ed_allocation(osv.osv):
    
    _name='vw.ed.allocation'
    _description ='Edumedia - Allocation Report'
    _auto=False
    _columns={ 
               'lines':fields.one2many('vw.ed.allocation.lines','main','Lines')
              }
vw_ed_allocation()

class vw_ed_allocation_lines(osv.osv):
    
    _name='vw.ed.allocation.lines'
    _description ='Edumedia - Allocation Report lines'
    _auto=False
    _columns={
               'department_id' : fields.many2one('hr.department','Department'),
               'job_id' :fields.many2one('hr.job','Designation'),
               'name' : fields.text('Name'),
               'main':fields.many2one('vw.ed.allocation','Main')
              }
    _order = "department_id"   
vw_ed_allocation_lines()

class ed_view_stock_rpt1(osv.osv):
    
    _name = 'ed.view.stock.rpt1' 
    _description = "Edumedia - Stock Report"
    _auto = False
    _columns = {    
         'name'  : fields.many2one('product.product', 'Component Id'), 
         'start_dt' : fields.date('Start Date'), 
         'end_dt' : fields.date('End Date'),
         'lines' : fields.one2many('ed.view.stock.rpt.lines', 'main', 'Lines')
        }
ed_view_stock_rpt1()

class ed_view_stock_rpt_lines(osv.osv):
    
    _name = 'ed.view.stock.rpt.lines' 
    _description = "Edumedia - Stock Report Lines/Details"
    _auto = False
    _columns = {     
             'main'  : fields.many2one('ed.view.stock.rpt1', 'Stock Parent Id'),    
             'seq' : fields.integer('Sequence'),   
             'stk_dt' : fields.date('Date'),
             'product_id': fields.many2one('product.product', 'Product'), 
             'detail': fields.char('Details', size=164),
             'opening' : fields.float('Opening Stock'),
             'arrival' : fields.float('Arrival'),  
             'issue' : fields.float('Issue'),
             'closing' : fields.float('Closing Stock'),
             'reference' : fields.char('Reference', size=300),         
        }
    
ed_view_stock_rpt_lines()

class ed_vw_appraisal_score(osv.osv):
    
    _name='ed.vw.appraisal.score'
    _description ='Edumedia-India- Appraisal Score'
    _auto=False
    _columns={'resource_id' : fields.many2one('ed.resource.appraisal','Resource Appraisal'),
              'lines':fields.one2many('ed.vw.appraisal.score.ln','main','Lines'),
              }
ed_vw_appraisal_score()

class ed_vw_appraisal_score_ln(osv.osv):
    
    _name='ed.vw.appraisal.score.ln'
    _description ='Edumedia-India- Appraisal Score Lines'
    _auto=False
    _columns={'summary_id' : fields.many2one('ed.app.overall','Overall Summary'),
              'main':fields.many2one('ed.vw.appraisal.score','Main'),
              }   
ed_vw_appraisal_score_ln()

class ed_vw_erp_implemantation(osv.osv):
    
    _name = 'ed.vw.erp.implemantation'
    _description = 'Edumedia-India - ERP-Implementation'
    _auto = False
    _columns={
              'start_dt' : fields.date('Start Date'), 
              'end_dt'   : fields.date('End Date'),
              'city_id'  : fields.many2one('ed.city','City'),
              'user_id'  : fields.many2one('res.users','Eduvisor'),
              'lines'    : fields.one2many('ed.vw.erp.implemantation.ln','main','Lines'),
              }
ed_vw_erp_implemantation()

class ed_vw_erp_implemantation_ln(osv.osv):
    
    _name = 'ed.vw.erp.implemantation.ln'
    _description = 'Edumedia-India - ERP-Implementation Lines'
    _auto = False
    _columns={
              'sale_id'     : fields.many2one('sale.order','Sale'),
              'cdd_id'      : fields.many2one('stock.picking','Cdd Delivery Order'),
              'workbk_id'   : fields.many2one('stock.picking','Work Book Delivery Order'),
              'scl_exist'   : fields.char('School Exists ?',size=64),
              'tot_stu'     : fields.integer('Total Students'),
              'price_unit'  : fields.float('Price'),
              'main'        : fields.many2one('ed.vw.erp.implemantation','Main'),
              }
ed_vw_erp_implemantation_ln()


