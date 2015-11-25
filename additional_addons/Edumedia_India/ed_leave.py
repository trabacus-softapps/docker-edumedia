from openerp.osv import fields,osv 
from openerp.tools.translate import _
import datetime
import time
from dateutil import parser
import re

class hr_holidays(osv.osv): 
    _inherit='hr.holidays' 
   
    def _compute_number_of_days(self, cr, uid, ids, name, args, context=None):
        result = {}
        for hol in self.browse(cr, uid, ids, context=context):
            if hol.type=='remove': 
                result[hol.id] = -hol.number_of_days_temp
            else:
                result[hol.id] = hol.number_of_days_temp
        return result 

    _columns = {
                'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Approved')],
                    'Status', readonly=True, track_visibility='onchange', copy=False,
                    help='The status is set to \'To Submit\', when a holiday request is created.\
                    \nThe status is \'To Approve\', when holiday request is confirmed by user.\
                    \nThe status is \'Refused\', when holiday request is refused by manager.\
                    \nThe status is \'Approved\', when holiday request is approved by manager.'),
                'payslip_status': fields.boolean(string='Reported in last payslips',
                    help='Green this button when the leave has been taken into account in the payslip.'),
                
                'ed_manager_id': fields.related('employee_id','manager_id',relation='hr.employee', string='Manager', type='many2one', store=True),
                'ed_manager_id2':fields.related('employee_id','manager2_id',relation='hr.employee', string = 'Manager2', type='many2one', store=True),
                'ed_manager_id3':fields.related('employee_id','manager3_id',relation='hr.employee', string = 'Manager3', type='many2one', store=True),
                'name': fields.char('Description', required=True, size=64),
                'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, help='Leave Manager can let this field empty if this leave request/allocation is for every employee'),
                'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=True,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
                'number_of_days_temp': fields.float('Number of Days', readonly=True, states={'draft':[('readonly',False)]}),
                'number_of_days': fields.function(_compute_number_of_days, method=True, string='Number of Days', store=True),
                'holiday_type': fields.selection([('employee','By Employee'),('category','By Employee Category')], 'Allocation Type', help='By Employee: Allocation/Request for individual Employee, By Employee Category: Allocation/Request for group of employees in category', required=True, states={'draft':[('readonly',False)]}),
                'date_from': fields.datetime('Start Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
                'date_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)],'confirm':[('readonly',False)]}),
                'notes': fields.text('Notes',readonly=True, states={'draft':[('readonly',False)],'confirm':[('readonly',False)]}),
                'aloc_date':fields.date('Allocation Date'),
                'fst_day':fields.boolean('Half Day', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]},help='Check this to apply First Day Half Leave.'),
                'sec_day':fields.boolean('Half Day', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]},help='Check this to apply Last Day Half Leave.'),
                
                }
    _order = 'date_from desc' 
    
    _sql_constraints = [
        ('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))", "You have to select an employee or a category"),
        ('date_check', "CHECK ( number_of_days_temp > 0 )", "The number of days must be greater than 0 !"),
        ('date_check2', "CHECK ( (type='add') OR (date_from <= date_to))", "The start date must be before the end date !")
    ]
    
    _defaults= {
                'state' : 'draft'
                }
    # TODO: can be improved using resource calendar method Overriden
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        diff_day = 0
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if date_from and date_to:
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            timedelta = to_dt - from_dt
            diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day
    #overriden
    def onchange_date_from(self, cr, uid, ids, chk_whch, date_to, date_from,first_day,sec_day):
        holObj = self.pool.get('ed.vw.holidays')
        User = self.pool.get('res.users').browse(cr, uid, uid)
        SatSunIds = []
        result = {}
        if date_to and date_from:
            datefrom = parser.parse(''.join((re.compile('\d')).findall(date_from)))
            dateto = parser.parse(''.join((re.compile('\d')).findall(date_to)))
            endday = ((parser.parse(''.join((re.compile('\d')).findall(date_to))))).strftime("%a").lower()
            diff_day = self._get_number_of_days(date_from, date_to)
            
            
            # to check is there any sunday in the date range also to get 2nd and 4th saturday 
            
            cr.execute("""
                    select a.* from 
                        (
                          select 
                              to_date(to_char(d,'YYYY-MM-DD'),'YYYY-MM-DD') as date, 
                              replace(to_char(d,'DAY'),' ','') as sat_day, 
                              extract(day from d), 
                              case when extract(day from d)  between 1 and 7 then 1 else 
                              case when extract(day from d)  between 8 and 14 then 2 else
                              case when extract(day from d)  between 15 and 21 then 3 else
                              case when extract(day from d)  between 22 and 28 then 4     
                              else 5 end end end end as weeks
                            from generate_series('""" +datefrom.strftime('%Y-%m-%d 00:00:00')+"""'::date, '""" +dateto.strftime('%Y-%m-%d 00:00:00')+"""'::date,'1day') g(d) 
                            where extract(dow from d) = 0 or extract(dow from d) = 6
                         )a
                     where a.sat_day ='SATURDAY' and a.weeks in (2,4) or a.sat_day ='SUNDAY'
            """)
            satSun = cr.fetchall()
            SatSunIds = [x[0] for x in satSun]
            if satSun and len(satSun) >=1:
                diff_day = diff_day - len(satSun)
            
            # to get list of holidays based on city
            holIds = holObj.search(cr, uid, [('h_date','>=',datefrom.strftime('%Y-%m-%d')),('h_date','<=',datefrom.strftime('%Y-%m-%d')),('city_id','=',User.city_id.id)])
            for h in holObj.browse(cr, uid, holIds):
                # checking if the holiday is saturday or sunday 
                if h.h_date not in SatSunIds:
                    diff_day = diff_day - 1
                
                
            no_days = round(diff_day) + 1
            if first_day: no_days -= 0.5
            if sec_day: no_days -= 0.5
            #if endday == 'sat': no_days += 1
            result['value'] = {
                               'date_from': datefrom.strftime('%Y-%m-%d 00:00:00'),
                               'date_to': dateto.strftime('%Y-%m-%d 00:00:00'),
                               'number_of_days_temp': no_days
                               }
            """ To uncheck the Half day check boxes. At any point only on check box should be active """
            if chk_whch == 'fst_day' and first_day:
                result['value'].update({'sec_day':False})
            if chk_whch == 'sec_day' and sec_day:
                result['value'].update({'fst_day':False})
            
            
            return result
            
        result['value'] = {
            'number_of_days_temp': 0,
        }
        return result
    
    
#overriden    
    def holidays_confirm(self, cr, uid, ids, context=None):
        print "context....", context
        for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
            
            if record.type=='remove' and context.get('send_mail'):
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'Edumedia_India', 'leave_request_send_mail')
                assert template._name == 'mail.template'
                mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, record.id, True, {})
        return self.write(cr, uid, ids, {'state': 'confirm'})
    
#    overriden
#     def holidays_confirm(self, cr, uid, ids, *args):
#         res = super(hr_holidays, self).holidays_confirm(cr, uid, ids)
#         reqst_obj = self.pool.get('res.request')
#         for case in self.browse(cr,uid,ids):
#         #Notification to Employee
#             req_ids=[]
#             if  case.type == 'remove':
#                 vals = { 
#                         'name': 'Leave Request'
#                        ,'act_to': case.employee_id.manager_id and case.employee_id.manager_id.user_id and case.employee_id.manager_id.user_id.id or False 
#                        ,'body':'Employee ' + str(case.employee_id.name) + ' has applied for leave. ' 
#                                ' Please do the need full.'
#                        ,'priority':'2'
#                         }
#                 if vals['act_to']: 
#                     #Mani
#                     #req_id = reqst_obj.create(cr, uid, vals)
#                     req_ids.append(req_id)
#                 
#                 vals['act_to'] = case.employee_id.manager2_id and case.employee_id.manager2_id.user_id and case.employee_id.manager2_id.user_id.id or False
#                 if vals['act_to']:                 
#                     #Mani
#                     #req_id = reqst_obj.create(cr, uid, vals)
#                     req_ids.append(req_id)
#                 
#                 vals['act_to'] = case.employee_id.manager3_id and case.employee_id.manager3_id.user_id and case.employee_id.manager3_id.user_id.id or False
#                 if vals['act_to']:                 
#                     #Mani
#                     #req_id = reqst_obj.create(cr, uid, vals)
#                     req_ids.append(req_id)
#                 
#                 # mani
#                 #reqst_obj.request_send(cr, uid, req_ids)
#                 if case.state == 'confirm':
#                     template = self.pool.get('ir.model.data').get_object(cr, uid, 'Edumedia_India', 'leave_request_send_mail')
#                     assert template._name == 'mail.template'
#                     mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, case.id, True, {})
#         return res
    
    def holidays_validate(self, cr, uid, ids, context=None):
        context = dict(context or {})
        Attend_obj = self.pool.get("ed.attendance")
        reqst_obj = self.pool.get('res.request')
        user_obj = self.pool.get('res.users')
        res = super(hr_holidays, self).holidays_validate(cr, uid, ids, context)         
        for case in self.browse(cr, uid, ids):
            absent_rec_ids = Attend_obj.search(cr,uid,[('employee_id','=',case.employee_id.id),('log_date','>=',case.date_from),('log_date','<=',case.date_to),('state','=','absent')])
            Attend_obj.write(cr, uid, absent_rec_ids, {'state':case.holiday_status_id.name,'remarks':case.name})
#            if absent_rec_ids:
#                for ab in Attend_obj.browse(cr,uid,absent_rec_ids):
#                    cr.execute("select extract(hour from '%s'::time - '%s'::time) as hrs"%(case.date_to,case.date_from))
#                    leave_hrs = cr.fetchone()
#                    day = 0 
#                    if case.holiday_status_id.type == 'paid':
#                       if leave_hrs[0] <= ab.wrk_hrs/2:
#                          day = 0.5
#                       else: 
#                          day = 1             
#                    Attend_obj.write(cr, uid, [ab.id],{'no_days':day,'state':case.holiday_status_id.type})
            man_name = user_obj.browse(cr,uid,uid).name
            
            if case.employee_id.user_id and case.type == 'remove':
                vals = { 
                        'name': 'Leave Request'
                       ,'act_to': case.employee_id.user_id and case.employee_id.user_id.id or False
                       ,'body':'Manager ' + str(man_name or '') + ' has approved your leave.' 
                       ,'priority':'2'
                        } 
#MANI
#                 req_id = reqst_obj.create(cr, uid, vals)                
#                 reqst_obj.request_send(cr, uid, [req_id])
                
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'Edumedia_India', 'leave_approved_send_mail')
                assert template._name == 'mail.template'
                mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, case.id, True, context=context)
            
        return res
    

    
    def holidays_refuse(self, cr, uid, ids, *args):
        Attend_obj = self.pool.get("ed.attendance")
        reqst_obj = self.pool.get('res.request')
        user_obj = self.pool.get('res.users')
        res = super(hr_holidays, self).holidays_refuse(cr, uid, ids)
        for case in self.browse(cr, uid, ids):
            absent_rec_ids = Attend_obj.search(cr,uid,[('employee_id','=',case.employee_id.id),('log_date','>=',case.date_from),('log_date','<=',case.date_to),('state','in',('paid','unpaid'))])
            Attend_obj.write(cr, uid, absent_rec_ids, {'state':'absent'})
            
            
            man_name = user_obj.browse(cr,uid,uid).name
            if case.employee_id.user_id and case.type == 'remove':
                vals = { 
                        'name': 'Leave Request'
                       ,'act_to': case.employee_id.user_id.id
                       ,'body':'Manager ' + str(man_name or '') + ' has refused your leave.' 
                       ,'priority':'2'
                        } 
# Mani                
#                 req_id = reqst_obj.create(cr, uid, vals)
#                 reqst_obj.request_send(cr, uid, [req_id])
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'Edumedia_India', 'leave_refuse_send_mail')
                assert template._name == 'mail.template'
                mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, case.id, True, {})
        return res
    
    def create(self, cr, uid, vals, context=None):
        context = dict(context or {})
        context.update({
                        'create': 1 
                        })
        vals.update({'state':'draft'})
        # to check the end date should not be less than start date
        if vals.get('date_from') and vals.get('date_to'):
            diff = self._get_number_of_days(vals.get('date_from'),vals.get('date_to'))
            if diff <0:
                raise osv.except_osv(_('Warning!'), _('The number of days must be greater than 0 !'))
                
        return super(hr_holidays,self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        context = dict(context or {})
        if context.get('create'):
            vals.update({'state' : 'draft'})
        
        for case in self.browse(cr, uid, ids):    
            # to check the end date should not be less than start date
            diff = self._get_number_of_days(vals.get('date_from',case.date_from),vals.get('date_to',case.date_to))
            if diff <0:
                raise osv.except_osv(_('Warning!'), _('The number of days must be greater than 0 !'))
        
        return super(hr_holidays, self).write(cr, uid, ids, vals, context)
    
hr_holidays()    


class ed_time_off(osv.osv):
    _name = "ed.time.off"
    
    def _employee_get(obj, cr, uid, context=None):
        ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        return ids and ids[0] or False

    _columns = {'ed_manager_id': fields.related('emp_id','manager_id',relation='hr.employee', string='Manager', type='many2one', store=True),
                'ed_manager_id2': fields.related('emp_id','manager2_id',relation='hr.employee', string='Manager2', type='many2one', store=True),
                'ed_manager_id3': fields.related('emp_id','manager3_id',relation='hr.employee', string='Manager3', type='many2one', store=True),
                'name' : fields.char('Description',size=500,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'emp_id' : fields.many2one('hr.employee','Employee',readonly=True),
                'start_date' : fields.datetime('Start Date',required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'end_date' : fields.datetime('End Date',required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'fst_day':fields.boolean('Half Day', readonly=True, states={'draft':[('readonly',False)]},help='Check this to apply First Day Half Leave.'),
                'sec_day':fields.boolean('Half Day', readonly=True, states={'draft':[('readonly',False)]},help='Check this to apply Last Day Half Leave.'),                
                'number_of_days_temp': fields.float('Number of Days', readonly=True, states={'draft':[('readonly',False)]}),
                'diff_time': fields.float('Hours', readonly=True, states={'draft':[('readonly',False)]}),
                'state': fields.selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
                        ('validate', 'Approved'), ('cancel', 'Cancelled')],'State',readonly=True),   
                'dummy_diff':fields.integer('Day Diff'),
                                                                           
                } 
    
    _defaults ={
                  'state': 'draft',
                  'emp_id': _employee_get,
                  'dummy_diff' : 1
                }    
    _order = 'start_date desc'
    
    _sql_constraints = [
        ('date_check', "CHECK ( number_of_days_temp > 0 )", "The number of days must be greater than 0 !"),
        ('date_check2', "CHECK (start_date <= end_date))", "The start date must be before the end date !")
    ]
    
    def _get_number_of_days(self, start_date, end_date):
        """Returns a float equals to the timedelta between two dates given as string."""
        
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(start_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(end_date, DATETIME_FORMAT)    
        timedelta = to_dt - from_dt
        days = timedelta.days + float(timedelta.seconds) / 86400
        return days
    
    def onchange_date_from(self, cr, uid, ids, chk_whch, start_date, end_date,first_day,sec_day):
        result = {}
        if start_date and end_date:
            diff_day = self._get_number_of_days(start_date, end_date)            
            cr.execute("""select (extract(hour from (select timestamp '"""  +  str(end_date) + """' - timestamp '""" + str(start_date) + """')))::int as Hours""")
            time_hrs = cr.fetchone() 
            no_days = round(diff_day) + 1
            if first_day: no_days -= 0.5
            if sec_day: no_days -= 0.5
            result['value'] = {
                'number_of_days_temp': no_days,
                'diff_time' : time_hrs[0],
                'dummy_diff' : int(diff_day)
            }
            """ To uncheck the Half day check boxes. At any point only on check box should be active """
            if chk_whch == 'fst_day' and first_day:
                result['value'].update({'sec_day':False})
            if chk_whch == 'sec_day' and sec_day:
                result['value'].update({'fst_day':False})
            
            return result
            
           
        result['value'] = {
            'number_of_days_temp': 0,
            'diff_time':0,
            'dummy_diff':1
        }
        return result
        
    def button_confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'confirm'})
        return True
    
    def button_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'cancel'}) 
        return True      
                             
    def button_setdraft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def button_refuse(self, cr, uid, ids, context={}):
        Attend_obj = self.pool.get("ed.attendance")
        self.write(cr, uid, ids, {'state': 'refuse'})
        for case in self.browse(cr, uid, ids):
            absent_rec_ids = Attend_obj.search(cr,uid,[('employee_id','=',case.emp_id.id),('log_date','>=',case.start_date),('log_date','<=',case.end_date)])
            Attend_obj.write(cr, uid, absent_rec_ids, {'state':'absent'})
        return True
    def button_validate(self, cr, uid, ids, context={}):
        Attend_obj = self.pool.get("ed.attendance")
        self.write(cr, uid, ids, {'state': 'validate'})
        for case in self.browse(cr, uid, ids):
            absent_rec_ids = Attend_obj.search(cr,uid,[('employee_id','=',case.emp_id.id),('log_date','>=',case.start_date),('log_date','<=',case.end_date),('state','=','absent')])
            Attend_obj.write(cr, uid, absent_rec_ids, {'state':'time_off','remarks':case.name})
        return True
    
    
    
ed_time_off()
