from openerp.osv import fields,osv
from openerp.tools.translate import _
import time 
import openerp.tools
from dateutil import parser
import re
from dateutil.relativedelta import relativedelta 
 
class hr_attendance(osv.osv): 
    _inherit = "hr.attendance"
    _columns = { 
                'manager_id': fields.related('employee_id','manager_id',relation='hr.employee', string='Manager', type='many2one', store=True),
                'manager_id2': fields.related('employee_id','manager2_id',relation='hr.employee', string='Manager2', type='many2one', store=True),
                'manager_id3': fields.related('employee_id','manager3_id',relation='hr.employee', string='Manager3', type='many2one', store=True),
                'validated_ok' : fields.boolean('Validated Record')
                
                }
    _defaults = {
                 'validated_ok' : False
                 } 
    
    #Overridden:
    def _altern_si_so(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_altern_si_so, 'Error: Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Warning!'),_('You cannot delete this record !')) 
        return super(hr.attendance, self).unlink(cr, uid, ids, context)

    
hr_attendance()

  
class ed_attendance(osv.osv):
    _name = "ed.attendance"
    _description = "Attendances "
    _columns = {
                'employee_id' : fields.many2one('hr.employee','Employee'),
                'manager_id': fields.related('employee_id','manager_id',relation='hr.employee', string='Manager', type='many2one', store=True),
                'manager_id2': fields.related('employee_id','manager2_id',relation='hr.employee', string='Manager2', type='many2one', store=True),
                'manager_id3': fields.related('employee_id','manager3_id',relation='hr.employee', string='Manager3', type='many2one', store=True),
                'log_date' : fields.date('Date'),
#                 'sign_in' : fields.time('Sign In'),
#                 'sign_out' : fields.time('Sign Out'),
                'sign_in' : fields.datetime('Sign In'),
                'sign_out' : fields.datetime('Sign Out'),
                'remarks' : fields.text("Remarks"),
                'no_days' : fields.float("Days"),
                'wrk_hrs' : fields.float("Actual Working Hrs"),
                'wrked_hrs' : fields.float("Worked Hrs"),
                'late_ok':fields.boolean('Late Log In/Out'),
                'state':fields.selection([('paid', 'Paid Leave'), ('unpaid', 'Unpaid Leave'),('holiday', 'Holiday')
                                          ,('present', 'Present'),('absent', 'Absent'),('time_off','Time Off')],'State',readonly=True),         
                }
    _defaults ={
                'no_days':1, 
               }    
    _order = 'log_date desc,employee_id'
    
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Warning!'),_('You cannot delete this record !'))
        return super(ed_attendance, self).unlink(cr, uid, ids, context)

    
#    def button_setdraft(self, cr, uid, ids, context={}):
#        self.write(cr, uid, ids, {'state': 'draft'})
#        return
    
    def button_approve(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'present'})
        return
    
    def button_refuse(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'no_days':0, 'state': 'absent'})
        return    
    
    def button_leave(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'leave'})
        return
    
ed_attendance() 

 
class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _description = "Employee"
    
#    def do_create_attendance(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
#    #def do_create_attendance(self, cr, uid, ids, context=None): 
#        edatt_obj = self.pool.get('ed.attendance')
#        HRlog_obj = self.pool.get('hr.attendance')
#        grace_obj = self.pool.get('ed.grace.signin')        
#        Hols_obj = self.pool.get('ed.holiday')               
#        Leave_obj = self.pool.get('hr.holidays')        
#        Log_obj = self.pool.get('ed.synchronization.log')
#        Time_obj = self.pool.get('ed.time.off')
##        print "%%%%%%%%%%%%%%%%%% I have been called", time.strftime("%H:%M:%S")
#        gperiod = 0      
#        gpid = grace_obj.search(cr, uid, [], limit=1)
#        if gpid:
#           gp = grace_obj.browse(cr, uid, gpid[0])
#           gperiod = gp.grace                   
#        cr.execute('select dt_time from ed_synchronization_log order by dt_time desc limit 1')
#        logtime = cr.fetchone()
#        if logtime:
#            getdate = logtime[0]
#            logdate = (parser.parse(getdate)+ relativedelta(hours =+ 24)).strftime('%Y-%m-%d')
#        else :
#            logdate = time.strftime("%Y-%m-%d")
#        emp_ids = self.search(cr, uid, [])
##        emp_ids = [1]
#        while( logdate <= time.strftime("%Y-%m-%d")): 
#            for case in self.browse(cr, uid, emp_ids):
#                siMaps = {}
#                soMaps = {}
#                lt_count = 0
#                bychkSI = ()
#                if case.emp_detail_ids:
#                   for e in case.emp_detail_ids: 
#                       siMaps.update({e.hr_day: e.hr_start_date})
#                       soMaps.update({e.hr_day: e.hr_end_date}) 
#                                   
#                currentday = ((parser.parse(''.join((re.compile('\d')).findall(logdate))))).strftime("%a").lower()
#                wrkday = siMaps.get(currentday, 'NonWorkingDay')
#                
#                TodaysLogs = HRlog_obj.search(cr, uid, [('employee_id','=',case.id)
#                                                           ,('name::date','=',logdate), ('validated_ok','=',False)], order = 'name') 
#     
#                Holidays = Hols_obj.search(cr, uid, [('city_id', '=',case.address_id.ed_city_id.id), ('h_date::date','=', logdate)])      
#                         
#                cr.execute("""SELECT hol.id FROM hr_holidays hol WHERE hol.employee_id = """ + str(case.id) + """ AND hol.state='validate'
#                                                                 AND '""" + str(logdate) + """' BETWEEN hol.date_from AND hol.date_to ORDER BY hol.id DESC;""")
#                LeaveRecords = cr.fetchone()
#                
#                ExistsTodaysLogs = edatt_obj.search(cr, uid, [('employee_id','=',case.id)
#                                                           ,('log_date::date','=',logdate)], order = 'name') 
#                
#                cr.execute("""SELECT tf.id FROM ed_time_off tf WHERE tf.emp_id = """ + str(case.id) + """ AND tf.state='validate'
#                                                           AND '""" + str(logdate) + """' BETWEEN tf.start_date AND tf.end_date order by tf.id DESC;""")
#                TimeoffLogs = cr.fetchone()
#                                    
#                if wrkday != 'NonWorkingDay':    
#                                      # ~~~~~~~~~~~~~~ Attendance on Holidays ~~~~~~~~~~~~~~
#                   if Holidays and not ExistsTodaysLogs:   
#                       edatt_obj.create(cr, uid, { 'employee_id': case.id
#                                                   , 'log_date':logdate
#                                                   , 'sign_in': time.strftime("00:00:00")
#                                                   , 'sign_out': time.strftime("00:00:00")
#                                                   , 'state': 'holiday' 
#                                                  })                    
#                       HRlog_obj.write(cr, uid, TodaysLogs, {'validated_ok':True})
#                       TodaysLogs = []
#                   
#                   elif  TimeoffLogs and wrkday != 'NonWorkingDay' and not ExistsTodaysLogs:
#                           edatt_obj.create(cr, uid, { 'employee_id': case.id
#                                                        , 'log_date':logdate
#                                                        , 'sign_in': time.strftime("00:00:00")
#                                                        , 'sign_out': time.strftime("00:00:00")
#                                                        , 'state': 'time_off'
#                                                        , 'no_days': 1  
#                                                       })
#                   
#                       # ~~~~~~~~~~~~~~ Absent Records ~~~~~~~~~~~~~~
#                   elif not TodaysLogs and wrkday != 'NonWorkingDay' and not ExistsTodaysLogs:
#                           edatt_obj.create(cr, uid, { 'employee_id': case.id
#                                                        , 'log_date':logdate
#                                                        , 'sign_in': time.strftime("00:00:00")
#                                                        , 'sign_out': time.strftime("00:00:00")
#                                                        , 'state': 'absent'
#                                                        , 'no_days': 1  
#                                                       })
#                               
#                       # ~~~~~~~~~~~~~~ Attendance from Log ~~~~~~~~~~~~~~                                  
#                   elif TodaysLogs:      
#                       
#                     for ha in HRlog_obj.browse(cr, uid, TodaysLogs):               
#                            
#                          if ha.action == 'sign_in': 
#                                
#                             edatt_obj.create(cr, uid, { 'employee_id': case.id,'log_date':ha.name, 'sign_in': ha.name })
#                             HRlog_obj.write(cr, uid, [ha.id], {'validated_ok':True})
#                                                          
#                          elif ha.action == 'sign_out':
#                                
#                               attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('sign_out','=',False)], order='sign_in desc', limit = 1)                     
#                               if attids:                                                      
#                                  rec = edatt_obj.browse(cr, uid, attids[0])
#                                  resval = {}
#                                  logday = ((parser.parse(''.join((re.compile('\d')).findall(ha.name))))).strftime("%a").lower()
#                                  logSItym = rec.sign_in
#                                  logSOtym = ((parser.parse(''.join((re.compile('\d')).findall(ha.name))))).strftime("%H:%M:00")
#                                                                 
#                                  wrkSItym = siMaps.get(((parser.parse(''.join((re.compile('\d')).findall(rec.log_date))))).strftime("%a").lower(), 'NonWorkingDay')
#                                  wrkSOtym = soMaps.get(logday, 'NonWorkingDay')                                                                
#                                                                            
#                                    # ~~~~~~~~~~~~~~ Worked Attendance as per Working days ~~~~~~~~~~~~~~   
#                                  
#                                  cr.execute("""select '""" + str(logSItym) + """'::time > '""" + str(wrkSItym) + """'::time 
#                                                and '""" + str(logSItym)+"""'::time <= ('""" + str(wrkSItym)+"""'::time + interval '""" + str(gperiod)+""" min')""")
#                                  ltchkSI = cr.fetchone()
#                                  
#                                  cr.execute("""select '""" + str(logSItym)+"""'::time > ('""" + str(wrkSItym)+"""'::time + interval '""" + str(gperiod)+""" min')""")
#                                  bychkSI = cr.fetchone()
#                                  
#                                  cr.execute("select '%s'::time < ('%s'::time - interval '%d min') "%(logSOtym, wrkSOtym, gperiod))
#                                  chkSO = cr.fetchone()   
#                                  
#                                  cr.execute("select extract(hour from '%s'::time - '%s'::time) as hrs"%(wrkSOtym, wrkSItym))
#                                  wrk_hrs = cr.fetchone()                                 
#                                 
#                                  cr.execute("select extract(hour from '%s'::time - '%s'::time) as hrs"%(logSOtym, logSItym))
#                                  wrked_hrs = cr.fetchone()
#                                  count = 0 
#                                  
#                                  if (ltchkSI and ltchkSI[0] == True) and case.late_count == 2:
#                                      lt_count = 3  
#                                  # Check Sign In  
#                                  if (ltchkSI and ltchkSI[0] == True or chkSO and chkSO[0] == True) and wrked_hrs >= wrk_hrs and case.late_count < 2:
#                                      count = case.late_count + 1
#                                      self.write(cr,uid,[case.id],{'late_count':count}) 
#                                      resval['state'] = 'present'
#                                      resval['remarks'] = 'Incorrect Login/out Time!!'
#                                      resval['late_ok'] = True
#                                  elif (ltchkSI and ltchkSI[0] == True or chkSO and chkSO[0] == True) and wrked_hrs < wrk_hrs: 
#                                      resval['state'] = 'absent'
#                                      resval['remarks'] = 'Incorrect Login/out Time!!'
#                                  elif (bychkSI and bychkSI[0] != True):
#                                      resval['state'] = 'present'
#                                      
#                                  resval['employee_id'] = case.id
#                                  resval['log_date'] = ha.name
#                                  resval['sign_out'] = ha.name
#                                  resval['wrk_hrs'] = wrk_hrs[0]
#                                  resval['wrked_hrs'] = wrked_hrs[0]
#                                  edatt_obj.write(cr, uid, attids, resval)
#                                  HRlog_obj.write(cr, uid, [ha.id], {'validated_ok':True})
#                                                              
#                                           
#                                                 
#                   
#                       # ~~~~~~~~~~~~~~ Leave Records ~~~~~~~~~~~~~~ha.day
#                   if LeaveRecords and not ExistsTodaysLogs:                                         
#                       
#                      for lr in Leave_obj.browse(cr,uid,[LeaveRecords[0]]):
#                           day = hfday = 0
#                           if lr.holiday_status_id.type == 'paid':
#                               day = 1
#                               hfday = 0.5
#                               
#                           if TodaysLogs:                                                  
#                                  attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('log_date','=',logdate)])                 
#                                  for rec in edatt_obj.browse(cr, uid, attids): 
#                                      resval = {}
#                                        # ~~~~~~~~~~ Full Day Absent ~~~~~~~~~
#                                      if rec.wrked_hrs < (rec.wrk_hrs / 2):
#                                          resval['state'] = lr.holiday_status_id.type
#                                          resval['no_days'] = day
#                                          resval['remarks'] = lr.name
#                                          # ~~~~~~~~~~~ Half Day Working ~~~~~~~~~~~~        
#                                      elif (rec.wrked_hrs > (rec.wrk_hrs / 2)) and (rec.wrked_hrs < rec.wrk_hrs):                                                     
#                                           resval['state'] = 'present'
#                                           resval['no_days'] = 0.5
#                                           resval['remarks'] = 'Half Working Day!!'
#                                           
#                                           # Half Day Leave
#                                           edatt_obj.create(cr, uid, { 'employee_id': case.id
#                                                                     , 'log_date':rec.log_date
#                                                                     , 'sign_in': time.strftime("00:00:00")
#                                                                     , 'sign_out': time.strftime("00:00:00")
#                                                                     , 'wrk_hrs' : rec.wrk_hrs
#                                                                     , 'wrked_hrs':rec.wrked_hrs
#                                                                     , 'state': lr.holiday_status_id.type 
#                                                                     , 'no_days': hfday
#                                                                     , 'remarks':lr.name
#                                                                     })
#                                                                                                     
#                                      edatt_obj.write(cr, uid, [rec.id], resval) 
#                           
#                           else :
#                               attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('log_date','=',logdate)])                 
#                               for rec in edatt_obj.browse(cr, uid, attids):       
#                                       edatt_obj.write(cr, uid, attids, {'state':lr.holiday_status_id.type,'no_days': day,'remarks':lr.name})
#                   
#                   else:
#                       if TodaysLogs:                                                  
#                                  attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('log_date','=',logdate)])                 
#                                  for rec in edatt_obj.browse(cr, uid, attids): 
#                                      resval = {}
#                                        # ~~~~~~~~~~ Full Day Absent ~~~~~~~~~
#                                      if rec.wrked_hrs < (rec.wrk_hrs / 2):
#                                          resval['state'] = 'absent'
#                                          resval['no_days'] = 1
#                                      
#                                          # ~~~~~~~~~~~ Half Day Working ~~~~~~~~~~~~        
#                                      elif ((rec.wrked_hrs > (rec.wrk_hrs / 2)) and (rec.wrked_hrs < rec.wrk_hrs)) or lt_count == 3 or (bychkSI and bychkSI[0] == True):                                                     
#                                           resval['state'] = 'present'
#                                           resval['no_days'] = 0.5
#                                           resval['remarks'] = 'Half Working Day!!'
#                                           
#                                           # Half Day Leave
#                                           edatt_obj.create(cr, uid, { 'employee_id': case.id
#                                                                     , 'log_date':rec.log_date
#                                                                     , 'sign_in': time.strftime("00:00:00")
#                                                                     , 'sign_out': time.strftime("00:00:00")
#                                                                     , 'wrk_hrs' : rec.wrk_hrs
#                                                                     , 'wrked_hrs':rec.wrked_hrs
#                                                                     , 'state': 'absent' 
#                                                                     , 'no_days': 0.5
#                                                                     })
#                                           if lt_count == 3:
#                                               self.write(cr,uid,[case.id],{'late_count':0})
#                                                                                                     
#                                      edatt_obj.write(cr, uid, [rec.id], resval)                
#            logdate = (parser.parse(logdate)+ relativedelta(hours =+ 24)).strftime('%Y-%m-%d')           
##            elif:
##                  # ~~~~~~~~~~~~~~ Compensated Attendance ~~~~~~~~~~~~~~                               
##                              if wrkSItym and wrkSOtym == 'NonWorkingDay':  
##                                  resval['state'] = 'present'
##                                  resval['remarks'] = 'Worked on Non-Working day.'
#        Log_obj.create(cr, uid, { 'dt_time':time.strftime("%Y-%m-%d %H:%M:%S'")})           
#        return True
    
    def _create_LeaveTimeRecords(self, cr, uid, ids, valslst, TodaysLogs, edatt_obj, context=None):
        """ Method will create Leave Records or Time Off records for the Employee """
        
        for case in self.browse(cr, uid, ids):     
           if TodaysLogs:                                                  
                  attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('log_date','=',valslst['logdate'])])                 
                  for rec in edatt_obj.browse(cr, uid, attids): 
                      resval = {}
                        # ~~~~~~~~~~ Full Day Absent ~~~~~~~~~
                      if rec.wrked_hrs < (rec.wrk_hrs / 2):
                          resval['state'] = valslst['state']
                          resval['no_days'] = valslst['day']
                      
                          # ~~~~~~~~~~~ Half Day Working ~~~~~~~~~~~~        
                      elif (rec.wrked_hrs > (rec.wrk_hrs / 2)) and (rec.wrked_hrs < rec.wrk_hrs):                                                     
                           resval['state'] = 'present'
                           resval['no_days'] = 0.5
                           resval['remarks'] = 'Half Working Day!!'
                           
                           # Half Day Leave
                           edatt_obj.create(cr, uid, { 'employee_id': case.id
                                                     , 'log_date':rec.log_date
                                                     , 'sign_in': time.strftime("00:00:00")
                                                     , 'sign_out': time.strftime("00:00:00")
                                                     , 'wrk_hrs' : rec.wrk_hrs
                                                     , 'wrked_hrs':rec.wrked_hrs
                                                     , 'state': valslst['state']
                                                     , 'no_days': valslst['hfday']
                                                     })
                                                                                     
                      edatt_obj.write(cr, uid, [rec.id], resval) 
                      
#                           =====================if applied for leave=================
           
           elif not TodaysLogs:
               attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('log_date','=',valslst['logdate'])])                 
                     
#                               ===================== if applied half day Leave and no sign in/out ===========
               days = 1  
               Half_day = False
               if valslst['date_from'] == valslst['logdate'] and valslst['fst_day']:
                  Half_day = True
                   
               if valslst['date_to'] == valslst['logdate'] and valslst['sec_day']:       
                   Half_day = True
                   
               if Half_day :
                  days = 0.5 
                  edatt_obj.create(cr, uid, { 'employee_id': case.id
                                                     , 'log_date': valslst['logdate']
                                                     , 'sign_in': time.strftime("00:00:00")
                                                     , 'sign_out': time.strftime("00:00:00")
                                                     , 'state': 'absent'
                                                     , 'no_days': 0.5
                                                     })
               for rec in edatt_obj.browse(cr, uid, attids):       
                    edatt_obj.write(cr, uid, attids, {'state': valslst['state'],'no_days': days,'remarks':valslst['descp']})

        return True
        
#    def do_create_attendance(self, cr, uid, ids, context=None):
    def do_create_attendance(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        edatt_obj = self.pool.get('ed.attendance')
        HRlog_obj = self.pool.get('hr.attendance')
        grace_obj = self.pool.get('ed.grace.signin')        
        Hols_obj = self.pool.get('ed.holiday')               
        Leave_obj = self.pool.get('hr.holidays')        
        Log_obj = self.pool.get('ed.synchronization.log')
        Time_obj = self.pool.get('ed.time.off')
        
        gperiod = 0      
        gpid = grace_obj.search(cr, uid, [], limit=1)
        if gpid:
           gp = grace_obj.browse(cr, uid, gpid[0])
           gperiod = gp.grace                   
        cr.execute('select dt_time from ed_synchronization_log order by dt_time desc limit 1')
        logtime = cr.fetchone()
        
        if logtime:
            getdate = logtime[0]
            logdate = (parser.parse(getdate)+ relativedelta(hours =+ 24)).strftime('%Y-%m-%d')
        else :
            logdate = time.strftime("%Y-%m-%d")
        emp_ids = self.search(cr, uid, [('active','=',True)])
#         emp_ids = [113]
#         logdate = '2015-08-20' 
    
        
        # to check the 2nd and 4th sat and also sunday
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
                            from generate_series('""" +time.strftime("%Y-%m-%d")+"""'::date, '""" +time.strftime("%Y-%m-%d")+"""'::date,'1day') g(d) 
                            where extract(dow from d) = 0 or extract(dow from d) = 6
                         )a
                     where a.sat_day ='SATURDAY' and a.weeks in (2,4) or a.sat_day ='SUNDAY'
            """)
        satSun = cr.fetchall()
        SatSunIds = [x[0] for x in satSun]
        if time.strftime("%Y-%m-%d") in SatSunIds:
            return

        while( logdate <= time.strftime("%Y-%m-%d")):
            for case in self.browse(cr, uid, emp_ids):
                siMaps = {}
                soMaps = {}                
                lt_count = 0
                chkSI = ()
                if case.emp_detail_ids:
                   for e in case.emp_detail_ids: 
                       siMaps.update({e.hr_day: e.hr_start_date})
                       soMaps.update({e.hr_day: e.hr_end_date}) 
                
               
                currentday = ((parser.parse(''.join((re.compile('\d')).findall(logdate))))).strftime("%a").lower()
                wrkday = siMaps.get(currentday, 'NonWorkingDay')
                
#                 cr.execute ("""select id from hr_attendance 
#                                            where id = (select max(id) from hr_attendance where  day = '""" + str(logdate) + """' and employee_id = """ + str(case.id) + """)
#                                            or id = (select min(id) from hr_attendance where  day = '""" + str(logdate) + """' and employee_id = """ + str(case.id) + """)
#                                            order by id """) 

                cr.execute ("""select id from hr_attendance 
                                           where id = (select max(id) from hr_attendance where  name::date = '""" + str(logdate) + """' and employee_id = """ + str(case.id) + """)
                                           or id = (select min(id) from hr_attendance where  name::date = '""" + str(logdate) + """' and employee_id = """ + str(case.id) + """)
                                           order by id """) 
                TodaysLogs =[]
                IOlogs = cr.fetchall()
                for lg in IOlogs:
                    TodaysLogs.append(lg[0])
     
     
                Holidays = Hols_obj.search(cr, uid, [('h_date','=', logdate)])
                               
                cr.execute("""SELECT hol.id FROM hr_holidays hol WHERE hol.employee_id = """ + str(case.id) + """ 
                                AND hol.state='validate'
                                AND '""" + str(logdate) + """' BETWEEN hol.date_from::date AND hol.date_to::date ORDER BY hol.id DESC;""")
                
                LeaveRecords = cr.fetchone()
                
#                 ExistsTodaysLogs = edatt_obj.search(cr, uid, [('employee_id','=',case.id)
#                                                              ,('log_date','=',logdate)], order = 'name') 
                
                ExistsTodaysLogs = edatt_obj.search(cr, uid, [('employee_id','=',case.id)
                                             ,('log_date','=',logdate)])
                
                cr.execute("""SELECT tf.id FROM ed_time_off tf WHERE tf.emp_id = """ + str(case.id) + """ AND tf.state='validate'
                                                           AND '""" + str(logdate) + """' BETWEEN tf.start_date::date AND tf.end_date::date order by tf.id DESC;""")
                TimeoffLogs = cr.fetchone()                  
                                    
                if wrkday != 'NonWorkingDay':    
                                      # ~~~~~~~~~~~~~~ Attendance on Holidays ~~~~~~~~~~~~~~
                   if Holidays and not ExistsTodaysLogs :    
                       edatt_obj.create(cr, uid, { 'employee_id': case.id
                                                   , 'log_date':logdate
                                                   , 'sign_in': time.strftime("%Y-%m-%d 00:00:00")# addes %Y-%m-%d" by mani
                                                   , 'sign_out': time.strftime("%Y-%m-%d 00:00:00")# addes %Y-%m-%d" by mani
                                                   , 'state': 'holiday' 
                                                  })                    
                       HRlog_obj.write(cr, uid, TodaysLogs, {'validated_ok':True})
                       TodaysLogs = []
                   
                                    
                       # ~~~~~~~~~~~~~~ Absent Records ~~~~~~~~~~~~~~    
                   elif not TodaysLogs and wrkday != 'NonWorkingDay' and not ExistsTodaysLogs:
                           edatt_obj.create(cr, uid, { 'employee_id': case.id
                                                        , 'log_date':logdate
                                                        , 'sign_in': time.strftime("%Y-%m-%d 00:00:00")# addes %Y-%m-%d" by mani
                                                        , 'sign_out': time.strftime("%Y-%m-%d 00:00:00")# addes %Y-%m-%d" by mani
                                                        , 'state': 'absent'
                                                        , 'no_days': 1  
                                                       })
                               
                       # ~~~~~~~~~~~~~~ Attendance from Log ~~~~~~~~~~~~~~                                  
                   elif TodaysLogs:      
                       
                     for ha in HRlog_obj.browse(cr, uid, TodaysLogs):               
                            
                          if ha.action == 'sign_in': 
                                
                             edatt_obj.create(cr, uid, { 'employee_id': case.id,'log_date':ha.name, 'sign_in': ha.name })
                             HRlog_obj.write(cr, uid, [ha.id], {'validated_ok':True})
                                                          
                          elif ha.action == 'sign_out':
                                
                               attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('sign_out','=',False),('log_date','=',logdate)], order='sign_in desc', limit = 1)   
                  
                                                 
                               if attids:                                                      
                                  rec = edatt_obj.browse(cr, uid, attids[0])
                                  resval = {}
                                  logday = ((parser.parse(''.join((re.compile('\d')).findall(ha.name))))).strftime("%a").lower()
                                  logSItym = rec.sign_in
                                  logSItym = ((parser.parse(''.join((re.compile('\d')).findall(rec.sign_in))))).strftime("%H:%M:%S")
                                  
                                  logSOtym = ((parser.parse(''.join((re.compile('\d')).findall(ha.name))))).strftime("%H:%M:00")
                                                                 
                                  wrkSItym = siMaps.get(((parser.parse(''.join((re.compile('\d')).findall(rec.log_date))))).strftime("%a").lower(), 'NonWorkingDay')
                                  wrkSOtym = soMaps.get(logday, 'NonWorkingDay')                                                                
                                                                            
                                    # ~~~~~~~~~~~~~~ Worked Attendance as per Working days ~~~~~~~~~~~~~~   
                                  
                                  cr.execute("""select '""" + str(logSItym) + """'::time > '""" + str(wrkSItym) + """'::time 
                                                and '""" + str(logSItym)+"""'::time <= ('""" + str(wrkSItym)+"""'::time + interval '""" + str(gperiod)+""" min')""")
                                  ltchkSI = cr.fetchone()

                                  
                                  cr.execute("select '%s'::time > ('%s'::time + interval '%d min') "%(logSItym, wrkSItym, gperiod))
                                  chkSI = cr.fetchone()
                                    
                                  cr.execute("select '%s'::time < '%s'::time "%(logSOtym, wrkSOtym))
                                  chkSO = cr.fetchone()   
                                  
                                  cr.execute("select extract(epoch from (('%s'::time - '%s'::time) - interval '%d min')) as hrs"%(wrkSOtym, wrkSItym,gperiod))
                                  wrk_hrs = cr.fetchone()                                 
                                 
                                  cr.execute("select extract(epoch from '%s'::time - '%s'::time) as hrs"%(logSOtym, logSItym))
                                  wrked_hrs = cr.fetchone()
                                  
                                  lt_count = 0
                                  
                                  if (ltchkSI and ltchkSI[0] == True) and case.late_count == 2:
                                      lt_count = 3
                                  # Check Sign In  
                                  if (ltchkSI and ltchkSI[0] == True or chkSO and chkSO[0] == True) and wrked_hrs >= wrk_hrs and case.late_count < 2:
                                      lt_count = case.late_count + 1
                                      self.write(cr,uid,[case.id],{'late_count':lt_count}) 
                                      resval['state'] = 'present'
                                      resval['remarks'] = 'Late Login/Logout !!'
                                      resval['late_ok'] = True
                                      
                                  else:
                                      resval['state'] = 'present'
                                      
                                  resval['employee_id'] = case.id
                                  resval['log_date'] = ha.name
                                  resval['sign_out'] = ha.name
                                  resval['wrk_hrs'] = wrk_hrs[0]
                                  resval['wrked_hrs'] = wrked_hrs[0]
                                  edatt_obj.write(cr, uid, attids, resval)
                                  HRlog_obj.write(cr, uid, [ha.id], {'validated_ok':True})
                                  
#                    ==========================if sign out time is not present===========              
                     attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('sign_out','=',False),('log_date','=',logdate)], order='sign_in desc', limit = 1)    
                            
                     if attids:   
                        resval = {} 
                        resval['state'] = 'absent'
                        resval['remarks'] = 'Sign out time unavailable'  
                        resval['no_days'] = 1                            
                        edatt_obj.write(cr, uid, attids, resval)
                                                 
                   
                       # ~~~~~~~~~~~~~~ Leave Records ~~~~~~~~~~~~~~
                   if LeaveRecords and not ExistsTodaysLogs:                                        
                       
                         for lr in Leave_obj.browse(cr,uid,[LeaveRecords[0]]):
                             day = hfday = 0
                             print "lr.holiday_status_id........",lr.holiday_status_id, case.id, logdate
                             if lr.holiday_status_id.name == 'paid':
                                 day = 1
                                 hfday = 0.5
                             
                             state = 'unpaid' if lr.holiday_status_id.limit else 'paid'                         
                             self._create_LeaveTimeRecords(cr, uid, [case.id], {'day': day, 'hfday':hfday, 'state': state, 'logdate':logdate
                                                                          , 'date_from': lr.date_from, 'date_to':lr.date_to, 'fst_day':lr.fst_day, 'sec_day':lr.sec_day,'descp':lr.name}
                                                           , TodaysLogs, edatt_obj, context)
                             
                   if TimeoffLogs and not ExistsTodaysLogs:                                        
                       
                       for to in Time_obj.browse(cr,uid,[TimeoffLogs[0]]):
                           self._create_LeaveTimeRecords(cr, uid, [case.id], {'day': 1 , 'hfday':0.5, 'state': 'time_off', 'logdate':logdate
                                                                          , 'date_from': to.start_date, 'date_to':to.end_date, 'fst_day':to.fst_day, 'sec_day':to.sec_day,'descp':to.name}
                                                           , TodaysLogs, edatt_obj, context)
                                    
                   elif not LeaveRecords and not TimeoffLogs:
                       if TodaysLogs:                                                  
                                  attids = edatt_obj.search(cr, uid, [('employee_id','=',case.id), ('log_date','=',logdate)])                 
                                  for rec in edatt_obj.browse(cr, uid, attids): 
                                      resval = {}
                                        # ~~~~~~~~~~ Full Day Absent ~~~~~~~~~
                                      if rec.wrked_hrs < (rec.wrk_hrs / 2):
                                          resval['state'] = 'absent'
                                          resval['no_days'] = 1
                                      
                                          # ~~~~~~~~~~~ Half Day Working ~~~~~~~~~~~~        
                                      elif (rec.wrked_hrs > (rec.wrk_hrs / 2)) and (rec.wrked_hrs < rec.wrk_hrs) or lt_count == 3 or (chkSI and chkSI[0] == True) :                                                     
                                           resval['state'] = 'present'
                                           resval['no_days'] = 0.5
                                           resval['remarks'] = 'Half Working Day!!'
                                           
                                           # Half Day Leave
                                           edatt_obj.create(cr, uid, { 'employee_id': case.id
                                                                     , 'log_date':rec.log_date
                                                                     , 'sign_in': time.strftime("%Y-%m-%d 00:00:00")
                                                                     , 'sign_out': time.strftime("%Y-%m-%d 00:00:00")
                                                                     , 'wrk_hrs' : rec.wrk_hrs
                                                                     , 'wrked_hrs':rec.wrked_hrs
                                                                     , 'state': 'absent' 
                                                                     , 'no_days': 0.5
                                                                     })
                                           
                                           if lt_count == 3:
                                               self.write(cr,uid,[case.id],{'late_count':0})
                                                                                                     
                                      edatt_obj.write(cr, uid, [rec.id], resval)      
                
                                          
            logdate = (parser.parse(logdate)+ relativedelta(hours =+ 24)).strftime('%Y-%m-%d')           
        Log_obj.create(cr, uid, { 'dt_time':time.strftime("%Y-%m-%d %H:%M:%S'")})           
        return True
    
    def do_create_earned_leaves(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
    #def do_create_earned_leaves(self, cr, uid, ids, context=None):
        Leave_obj = self.pool.get('hr.holidays')
        emp_obj = self.pool.get('hr.employee')
        emp_ids = self.search(cr, uid, [])
        holstat_obj = self.pool.get('hr.holidays.status')
        holstat_id = holstat_obj.search(cr,uid,[('name','=','Earned Leave')])
        holstat_id = holstat_id and holstat_id[0] or False
        
        for case in emp_obj.browse(cr,uid,emp_ids):
            lv_alloc_ids = Leave_obj.search(cr,uid,[('aloc_date','<=',time.strftime("%Y-%m-%d %H:%M:%S'")),('employee_id','=',case.id),('type','=','add'),('state','=','validate')])
            if lv_alloc_ids:
               alloc_date = Leave_obj.browse(cr,uid,lv_alloc_ids[0]).aloc_date
               if alloc_date:
                  alloc_month = ((parser.parse(''.join((re.compile('\d')).findall(alloc_date))))).strftime("%m")
                  if case.ac_conform_due_date:
                        actual_con_date = ((parser.parse(''.join((re.compile('\d')).findall(case.ac_conform_due_date))))).strftime("%Y-%m-%d")
                        if  actual_con_date < time.strftime("%Y-%m-%d") and time.strftime("%m") > alloc_month:
                           Leave_id = Leave_obj.create(cr,uid,{'name':'Leave Credited for Month'
                                                    ,'employee_id':case.id
                                                    ,'holiday_status_id':holstat_id
                                                    ,'number_of_days_temp':2.0
                                                    ,'type':'add'
                                                    ,'aloc_date':time.strftime("%Y-%m-%d")
                                                    ,'state':'draft'})
                           Leave_obj.holidays_confirm( cr, uid, [Leave_id])
                           Leave_obj.holidays_validate(cr, uid, [Leave_id], context) 
                           
            elif case.ac_conform_due_date:
                actual_con_date = ((parser.parse(''.join((re.compile('\d')).findall(case.ac_conform_due_date))))).strftime("%Y-%m-%d")
                if  actual_con_date < time.strftime("%Y-%m-%d"):
                   Leave_id = Leave_obj.create(cr,uid,{'name':'Leave Credited for Month'
                                            ,'employee_id':case.id
                                            ,'holiday_status_id':holstat_id
                                            ,'number_of_days_temp':2.0
                                            ,'type':'add'
                                            ,'aloc_date':time.strftime("%Y-%m-%d")
                                            ,'state':'draft'})
                   Leave_obj.holidays_confirm( cr, uid, [Leave_id])
                   Leave_obj.holidays_validate(cr, uid, [Leave_id], context)    
        return True
    
    def do_remainder_mail(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
    #def do_remainder_mail(self, cr, uid, ids, context=None):
        Leave_obj = self.pool.get('hr.holidays')
        Tmoff_obj = self.pool.get('ed.time.off')
        Atten_obj = self.pool.get('ed.attendance')
        emp_obj = self.pool.get('hr.employee')
        emp_ids = self.search(cr, uid, [])
        for case in emp_obj.browse(cr,uid,emp_ids):     
            Leave_rec_ids = Leave_obj.search(cr,uid,[('ed_manager_id','=',case.id),('type','=','remove'),('state','=','confirm'),('date_from','>=',time.strftime("%Y-%m-%d 00:00:00'"))])
            Absent_rec_ids = Atten_obj.search(cr,uid,[('employee_id','=',case.id),('state','=','absent')])
            Tmoff_rec_ids = Tmoff_obj.search(cr,uid,[('ed_manager_id','=',case.id),('state','=','confirm'),('start_date','>=',time.strftime("%Y-%m-%d 00:00:00'"))])
        
            if len(Leave_rec_ids) > 0:
               self.action_send(cr, uid, [case.id],'leave', context) 
            if len(Tmoff_rec_ids) > 0:
                self.action_send(cr, uid, [case.id],'timeoff', context)
            if len(Absent_rec_ids) > 0:
                self.action_send(cr, uid, [case.id],'absent', context)
        return True        
                    
    def action_send(self, cr, uid, ids,type, context=None):
        """ This sends an email to respective heads requesting for leave
        """        
        mail_obj = self.pool.get('crm.send.mail')
        Addr_obj = self.pool.get('res.partner')
        user = self.pool.get('res.users').browse(cr, uid,uid)
        for case in self.browse(cr,uid,ids):
            subtype = 'plain'
            comp_email = ''
            if case.company_id:
               #addr_id = Addr_obj.search(cr,uid,[('partner_id','=',case.company_id.id)])[0]
               comp_email = case.company_id.email 
            email_to = case.work_email
            email_from = comp_email
            email_cc = comp_email
            
#            if not email_from:
#                raise osv.except_osv(_('Error'), _("Please enter " + str(case.user_id.name) + "'s Email id!"))
#                
#            if not email_to:
#                raise osv.except_osv(_('Error'), _("Please enter " + str(case.employee_id.name) + "'s Email id!"))
#                
            emails = re.findall(r'([^ ,<@]+@[^> ,]+)', email_to or '')
            email_cc = re.findall(r'([^ ,<@]+@[^> ,]+)', email_cc or '')
            emails = filter(None, emails)
            if type == 'leave':  
                subject = 'Reminder for Approval of Leave Requests'
                body = ""
                body += """\n\n Dear """ + (case.name or '-') + """,\n\n""" 
                body += """ There are employee leave requests waiting for your approval. Please login to the Edumedia ERP and approve the same using the Human Resources link.\n\n"""
                body += """ Regards, \n\n The Edumedia HR Team."""    
                             
            if type == 'timeoff':
                subject = 'Reminder for Approval of Time Off Requests'  
                body = ""
                body += """ Dear """ + (case.name or '-') + """,\n\n""" 
                body += """ There are employee time-off requests waiting for your approval. Please login to the Edumedia ERP and approve the same using the Human Resources link.\n\n""" 
                body += """ Regards, \n\n The Edumedia HR Team.""" 
                
            if type == 'absent':
                subject = 'Absent Records'  
                body = ""                
                body += """\n\nDear """ + (case.name or '-') + """,\n\n""" 
                body += """ There are Absent records against your name. Please login to Edumedia ERP and apply for leave/time-off. Please note Absent records affect your salary.\n\n""" 
                body += """ Regards, \n\n The Edumedia HR Team.""" 
                
            if emails and email_from: 
                flag = openerp.tools.email_send(
                    email_from,
                    emails,
                    subject, 
                    body,
                    email_cc = email_cc,
                    #attach = [],
                    subtype = subtype,
                    reply_to = email_from,
                    openobject_id = str(case.id),
                    headers = {}
                )

                if not flag:
                    raise osv.except_osv(_('Error!'), _('Unable to send mail. Please check SMTP is configured properly.'))
 
        return True

        
hr_employee()     
    

class ed_grace_signin(osv.osv):
    _name = "ed.grace.signin"
    _description = "Grace Period Sign In"
    _columns = {
                'grace' :fields.integer('Sign In - Grace Period (in Min.)'),
                }
ed_grace_signin()    
                