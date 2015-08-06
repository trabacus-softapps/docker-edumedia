from openerp.osv import fields,osv
import time
import config 
from openerp.tools.translate import _

EmpApp_STATES =  [('draft','Draft'),
                  ('emp_submit','Submitted by Employee'),
                  ('emp_timeout','Time Out'),
                  ('man_acpt','Approved by Manager'),
                  ('man_timeout','Time Outmmmmmmmmmmm'), 
                  ('hr_acpt','Approved by HR'),
                  ('done','Done'),
                  ('cancel','Cancelled')]

POINTS = [
    (0,'0'),          
    (1,'1'),
    (2,'2'),
    (3,'3'), 
    (4,'4'), 
    (5,'5'),
    (6,'6'),
    (7,'7'),
    (8,'8'),
    (9,'9'),
    (10,'10'),
]
 

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _description = "Employee"
        
    def _state(self, cr, uid, ids, name, args, context=None):
        result = {}
        if not ids:
            return result
        for id in ids:
            result[id] = 'absent'
        cr.execute('SELECT hr_attendance.action, hr_attendance.employee_id \
                FROM ( \
                    SELECT MAX(name) AS name, employee_id \
                    FROM hr_attendance \
                    WHERE action in (\'sign_in\', \'sign_out\') \
                    and name::date = now()::date GROUP BY employee_id \
                ) AS foo \
                LEFT JOIN hr_attendance \
                    ON (hr_attendance.employee_id = foo.employee_id \
                        AND hr_attendance.name = foo.name) \
                WHERE hr_attendance.employee_id IN %s',(tuple(ids),))
        for res in cr.fetchall():
            result[res[1]] = res[0] == 'sign_in' and 'present' or 'absent'
        return result
    
     
        
    _columns = {      
                 'manager_id' : fields.many2one('hr.employee','Manager'), 
                 'manager2_id' : fields.many2one('hr.employee','Manager2'), 
                 'manager3_id' : fields.many2one('hr.employee','Manager3'), 
                 'emp_detail_ids' : fields.one2many('ed.hr.emp.details','hr_emp_id','Employee',ondelete = 'cascade'),
                 'date_of_join' : fields.date('Date of Joining'),
                 'contract_ids'  :fields.one2many('hr.contract','employee_id','Contracts'),
                 'conform_due_date' : fields.date('Conformation Due Date'),
                 'ac_conform_due_date' : fields.date('Actual Conformation Date'),
                 'leave_date' : fields.date('Date of Leaving'),
                 'pan_no' : fields.char('PAN NO',size=50),
                 'esic_no' : fields.char('ESIC NO',size=50),
                 'state': fields.function(_state, method=True, type='selection', selection=[('absent', 'Absent'), ('present', 'Present')], string='Attendance'),
                 'peer_emp_ids': fields.many2many('hr.employee', 'peer_emp_rel', 'peer_id', 'emp_id', 'Peer'),
                 'super_emp_ids':fields.many2many('hr.employee','super_emp_rel','super_id','emp_id','Supervisor'),
                 'pf_no':fields.char('PF Account No',size=15),
                 'late_count':fields.integer('Late Count'),
                 'emp_alloc_ids' : fields.one2many('ed.hr.allocation','hr_emp_id','Allocation',ondelete = 'cascade'),
                 
                 } 
 
    
    def create(self, cr, uid, vals, context=None):
        partner_id = False
        detail_obj = self.pool.get('ed.hr.emp.details')
        work_obj = self.pool.get('ed.company.work.time')
        obj_partner = self.pool.get('res.partner')
        hol_obj = self.pool.get('hr.holidays')
        wrktime_ids = []
        if 'department_id' in vals :
           wrktime_ids = work_obj.search(cr,uid,[('depat_id','=',vals['department_id'])])
        emp_id=super(hr_employee, self).create(cr, uid, vals, context)
        
        for wr in work_obj.browse(cr,uid,wrktime_ids):
            detail_obj.create(cr,uid,{'hr_emp_id' : emp_id,
                             'hr_day' : wr.hr_day,
                             'hr_start_date':wr.hr_start_date,
                             'hr_end_date':wr.hr_end_date,
                             }) 
        if not vals.get('name', False) or vals.get('partner_id', False):
            self.cache_restart(cr)
            return emp_id
                        
        partner_id = obj_partner.create(cr, uid, {'name': vals['name'],'employee':True,'customer':False}, context=context)
        vals.update({'partner_id': partner_id})
        
        return emp_id
    
    def update_worktimings(self, cr, uid, ids,department_id,context=None): 
        detail_obj = self.pool.get('ed.hr.emp.details')
        work_obj = self.pool.get('ed.company.work.time')
        obj_partner = self.pool.get('res.partner')
        hol_obj = self.pool.get('hr.holidays')
        dep_wrk = set()
        deptwk_dict = {}
        emp_wrk = set()
        empwk_dict = {}
        
        depwrktm_ids = work_obj.search(cr,uid,[('depat_id','=',department_id)])  
        for case in self.browse(cr,uid,ids):
            for ed in case.emp_detail_ids:
                emp_wrk.add(ed.hr_day)
                empwk_dict[ed.hr_day] = ed.id

            for wr in work_obj.browse(cr,uid, depwrktm_ids):
                dep_wrk.add(wr.hr_day)
                deptwk_dict[wr.hr_day] =wr.id
                
            for d in dep_wrk:                 
                start_dt = work_obj.browse(cr,uid,deptwk_dict[d]).hr_start_date
                end_dt = work_obj.browse(cr,uid,deptwk_dict[d]).hr_end_date
                  
                # Updating Existing    
                if d in empwk_dict.keys():
                    detail_obj.write(cr,uid,[empwk_dict[d]], {'hr_start_date':start_dt,'hr_end_date':end_dt})
                # Inserting new records
                else:                               
                     detail_obj.create(cr,uid,{'hr_emp_id' : case.id,
                             'hr_day' : d,
                             'hr_start_date':start_dt,
                             'hr_end_date':end_dt,
                             }) 
            # deleting 
            if emp_wrk.difference(dep_wrk):
                emp_wrk1 = emp_wrk.difference(dep_wrk)
                for e in emp_wrk1:
                    detail_obj.unlink(cr,uid,[empwk_dict[e]])
        return True
 
    def write(self, cr, uid, ids,vals,context=None): 
        work_obj = self.pool.get('ed.company.work.time')
        
        for case in self.browse(cr,uid,ids):
            if 'department_id' in vals:
                if vals['department_id'] != case.department_id.id:
                    self.update_worktimings(cr, uid, ids, vals['department_id'],context)                      
         
        return super(hr_employee, self).write(cr, uid, ids, vals,context)           

    
hr_employee()     
 
class ed_hr_emp_details(osv.osv):
    _name = 'ed.hr.emp.details'
    _description = 'HR Employee Details'
    
    def _gen_sequence(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        
        for case in self.browse(cr,uid,ids):
            seq = 0
            if case.hr_day == 'mon':seq = 1
            elif case.hr_day == 'tue':seq = 2
            elif case.hr_day == 'wed':seq = 2
            elif case.hr_day == 'thu':seq = 2
            elif case.hr_day == 'fri':seq = 2
            elif case.hr_day == 'sat':seq = 2
            elif case.hr_day == 'sun':seq = 2    
            res[case.id] = seq
        return res
    
    _columns = {
                'hr_emp_id' : fields.many2one('hr.employee','Employee Details',ondelete = 'cascade'),
                'hr_day' : fields.selection([('mon','Monday'),('tue','Tuesday'),('wed','Wednesday'),('thu','Thrusday'),('fri','Friday'),('sat','Saturday'),('sun','Sunday')],'Days'),
#                 'hr_start_date' : fields.time('Start Time'),
#                 'hr_end_date' : fields.time('End Time'),
                'hr_start_date' : fields.datetime('Start Time'),
                'hr_end_date' : fields.datetime('End Time'),
                'seq': fields.function(_gen_sequence, string='Sequence', method=True, store=True, type='integer'),
                }
    _order = 'seq'
    
ed_hr_emp_details() 


class ed_holiday(osv.osv):
    _name = 'ed.holiday'
    _descrption = 'Holidays'
    _columns = {
                'name' : fields.char('Holiday Name',size=100, required=True),
                'city_id':fields.many2one('ed.city', 'City', required=True),
                'h_date' : fields.date('Date')
                } 
ed_holiday() 
  

class ed_resource_appraisal(osv.osv):
    _name = 'ed.resource.appraisal'
    _description = 'H Resource Appraisals'
        
    _columns = {
                 'fiscal_year' : fields.many2one('account.fiscalyear','Financial Year', required=True, readonly=True,states={'draft': [('readonly', False)]}),
                 'start_date' :fields.date('Start Date', required=True, readonly=True,states={'draft': [('readonly', False)]}),
                 'end_date' : fields.date('End Date', required=True, readonly=True,states={'draft': [('readonly', False)]}),
                 'emp_end_date' : fields.date('Employee End Date', required=True, ),
                 'man_end_date' :fields.date('Manager End Date', required=True, ),
                 'name' : fields.char('Description',size=500,readonly=True,states={'draft': [('readonly', False)]}),
                 'hr_dept_ids':fields.many2many('hr.department','app_dept_rel','resource_id','depart_id','Department',readonly=True,states={'draft': [('readonly', False)]}),                  
                 'state' : fields.selection([('draft','Draft'),('in_progress','In Progress'),('fps_cycle','Finish Peer/Supervisor Cycle'),('f_cycle','Finish Cycle'),('done','done')],'State'),
               }      
    _defaults = {
                'state' :  lambda *a: 'draft',
                }
    
    def unlink(self, cr, uid, ids, context=None):
        for case in  self.browse(cr,uid,ids):
            if case.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete this record !')) 
        return super(ed_resource_appraisal, self).unlink(cr, uid, ids, context)
    
    def button_startcycle(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'in_progress'})
        Emp_obj = self.pool.get('hr.employee')
        EmpApp_obj = self.pool.get('ed.appraisal')
        Ini_obj = self.pool.get('ed.initiator')
        AppIni_obj = self.pool.get('ed.app.initiator') 
        Skill_obj = self.pool.get('ed.skill.behave')
        AppSkill_obj = self.pool.get('ed.app.skills.behave') 
        Train_obj = self.pool.get('ed.hr.training')
        AppTrain_obj = self.pool.get('ed.app.training') 
        Asss_obj = self.pool.get('ed.hr.assess')
        AppAsss_obj = self.pool.get('ed.app.hr.assess') 
        KPIset_obj = self.pool.get('ed.app.kpi.nxt.years') 
        KPI_obj = self.pool.get('ed.app.kpi.current.years') 
        Ovr_obj = self.pool.get('ed.app.overall')
        reqst_obj = self.pool.get('res.request')
        Dept_obj = self.pool.get('hr.department')
        
        empids = Emp_obj.search(cr, uid, [])
        iids = Ini_obj.search(cr, uid, []) 
        skids = Skill_obj.search(cr, uid, []) 
        asids = Asss_obj.search(cr, uid, [])
        trids = Train_obj.search(cr,uid,[])
        EmpAppids = []
        for case in self.browse(cr, uid, ids):
#            existids = self.search(cr, uid, [('state', '=', 'in_progress'),('id','!=',case.id)])
#            if existids:
#                raise osv.except_osv(_('warning'),('Please close the existing Appraisal to start this!!!'))
#                return False
            
            for a in case.hr_dept_ids: 
                for de in Dept_obj.browse(cr,uid,[a.id]):          
                    for emp in de.member_ids:
                        EmpAppid = EmpApp_obj.create(cr, uid, {
                                                         'emp_id'    : emp.id,
                                                         'manager_id': emp.manager_id.id or False,
                                                         'manager_id2':emp.manager2_id.id or False,
                                                         'manager_id3':emp.manager3_id.id or False,
                                                         'start_date': case.start_date,
                                                         'end_date'  : case.end_date,
                                                         'man_end_date':case.man_end_date,
                                                         'emp_end_date':case.emp_end_date,
                                                         'name': case.name,
                                                         'resource_id':case.id,
                                                         })
                        EmpAppids.append(EmpAppid)
                        
                        for i in Ini_obj.browse(cr, uid, iids):
                             AppIni_obj.create(cr, uid
                                                 , {'initiate_ques' : i.name,  
                                                    'appraisal_id'  : EmpAppid
                                                   })
                        
                        for sk in Skill_obj.browse(cr, uid, skids):
                             AppSkill_obj.create(cr, uid
                                                 , {'p1_ques'  : sk.name, 
                                                    'p1_desc'  : sk.desc,
                                                    'appraisal_id': EmpAppid
                                                   })
                             
                        for tr in Train_obj.browse(cr, uid, trids):
                             AppTrain_obj.create(cr, uid
                                                 , {'train_ques'  : tr.name,                                           
                                                    'appraisal_id': EmpAppid
                                                   })
                             
                        for a in Asss_obj.browse(cr, uid, asids):
                             AppAsss_obj.create(cr, uid
                                                 , {'hr_param' : a.name,  
                                                    'hr_outof' : a.out_of,
                                                    'appraisal_id': EmpAppid
                                                   })
                             
                        previds = EmpApp_obj.search(cr, uid, [('emp_id', '=', emp.id), ('state','not in',('draft','cancel'))], order = 'start_date desc', limit = 1)     
                        kpids = KPIset_obj.search(cr, uid, [('appraisal_id', 'in', previds)])
                        for k in KPIset_obj.browse(cr, uid , kpids):
                            KPI_obj.create(cr, uid, {
                                                     'department_id' : k.department_id.id,
                                                     'desc_text'  : k.desc_text,
                                                     'report_to'  : k.report_to,
                                                     'weights'    : k.weights,
                                                     'appraisal_id':EmpAppid
                                                     })
                        
                        for par in ['Skills & Behaviour', 'Competency Assessment', 'KPI','Human Resource Assessment']:
                            Ovr_obj.create(cr, uid, {
                                                     'eval_param':par,
                                                     'appraisal_id':EmpAppid                                             
                                                     })
                        #Notification to Employee
                        if emp.user_id:
                            vals = { 
                                        'name':'Appraisal Cycle Started'
                                       ,'act_to': emp.user_id.id
                                       ,'body':'The appraisal cycle for the period ' + str(case.start_date) + 
                                               ' to ' + str(case.end_date) + ' has started. Please visit the ' 
                                               'My Appraisal link of the HR menu to enter your remarks.'
                                       ,'priority':'2'
                                         } 
                            req_id = reqst_obj.create(cr, uid, vals)
                            reqst_obj.request_send(cr, uid, [req_id])
                                
                    EmpApp_obj.write(cr, uid, EmpAppids, {})
        return True
    
    def button_start_peersupervisor_cycle(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state': 'fps_cycle'})
        Emp_obj = self.pool.get('hr.employee')
        Dept_obj = self.pool.get('hr.department')
        Param_obj = self.pool.get('ed.peersuper.parameters')
        peer_obj = self.pool.get('ed.peersuper.appraisal') 
        peerln_obj = self.pool.get('ed.peersuper.appraisal.line')
        peer_ques_ids = Param_obj.search(cr,uid,[('type','=','peer')])
        super_ques_ids = Param_obj.search(cr,uid,[('type','=','supervisor')])
        reqst_obj = self.pool.get('res.request')
        p = [] 
        s = []
        for case in self.browse(cr, uid, ids): 
            for a in case.hr_dept_ids: 
                for de in Dept_obj.browse(cr,uid,[a.id]):
                    for mem in de.member_ids:
                        for peer in mem.peer_emp_ids:
                            Emp_peer_id = Emp_obj.search(cr,uid,[('id','=',peer.id)])[0]
                            peer_id = peer_obj.create(cr,uid,{'rate_by_id':Emp_peer_id
                                                        ,'rate_for_id':mem.id
                                                        ,'resource_id':case.id
                                                        ,'name':case.name
                                                        ,'type':'peer'
                                                        ,'state':'draft'})
                            if peer_id:
                                for pq in peer_ques_ids:
                                    peerln_obj.create(cr,uid,{'peersuper_id':peer_id
                                                              ,'psparameters_id': pq
                                                              ,'rating':0})
                        for super in mem.super_emp_ids:
                            Emp_super_id = Emp_obj.search(cr,uid,[('id','=',super.id)])[0]
                            super_id = peer_obj.create(cr,uid,{'rate_by_id':Emp_super_id
                                                        ,'rate_for_id':mem.id
                                                        ,'resource_id':case.id
                                                        ,'name':case.name
                                                        ,'type':'supervisor'
                                                        ,'state':'draft'})
                            if super_id:
                                for sq in super_ques_ids:
                                    peerln_obj.create(cr,uid,{'peersuper_id':super_id
                                                              ,'psparameters_id': sq
                                                              ,'rating':0})
                        
                        
                        #Notification to Employee
                        if mem.user_id:
                            vals = { 
                                    'name': ' Peer/Supervisor Appraisal Cycle Started'
                                   ,'act_to': mem.user_id.id
                                   ,'body':'The Peer/Supervisor Appraisal cycle has started.'
                                           ' Please visit the Peer/Supervisor Appraisal link of the HR menu immediately to enter your remarks.'
                                   ,'priority':'2'
                                    } 
                            req_id = reqst_obj.create(cr, uid, vals)
                            reqst_obj.request_send(cr, uid, [req_id])    
                        
        return True
    
    def button_peer_supervisor_finish(self, cr, uid, ids, context={}):
        peer_obj = self.pool.get('ed.peersuper.appraisal') 
        self.write(cr, uid, ids, {'state': 'f_cycle'})
        for case in self.browse(cr,uid,ids):
            peer_ids = peer_obj.search(cr,uid,[('resource_id','=',case.id)])
            for po in peer_ids:
                peer_obj.write(cr, uid, [po], {'state': 'done'})
        
        return True
    
    def button_finish(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'done'})
        return True
    
    def button_updateEmpdate(self, cr, uid, ids, context={}):
        EmpApp_obj = self.pool.get('ed.appraisal')
        for case in self.browse(cr, uid, ids):
            aids = EmpApp_obj.search(cr, uid, [('resource_id','=', case.id)])
            EmpApp_obj.write(cr, uid, aids, {})
            
            for e in EmpApp_obj.browse(cr, uid, aids):
                aevals = {}
                aevals['emp_end_date'] = case.emp_end_date
                if e.state == 'emp_timeout':
                    aevals['state'] = 'draft'
                EmpApp_obj.write(cr,uid,[e.id], aevals)
        return True
    
    def button_updateMandate(self, cr, uid, ids, context={}):
        EmpApp_obj = self.pool.get('ed.appraisal')
        for case in self.browse(cr, uid, ids):
            aids = EmpApp_obj.search(cr, uid, [('resource_id','=', case.id)])
            EmpApp_obj.write(cr, uid, aids, {})
            
            for e in EmpApp_obj.browse(cr, uid, aids):
                aevals = {}
                aevals['man_end_date'] = case.man_end_date
                if e.state == 'man_timeout':
                    aevals['state'] = 'emp_submit'
                EmpApp_obj.write(cr,uid,[e.id], aevals)
        return True
    
ed_resource_appraisal() 

class ed_appraisal(osv.osv):
    _name = 'ed.appraisal'
    _description = 'Employee Appraisals'
        
    def _get_all_points(self, cr, uid, ids, name, args, context=None):
        res = {}
        maxval = 0.00
        perf_obj = self.pool.get('ed.performance.review')
        perf_id = perf_obj.search(cr, uid, [], limit = 1)
        if perf_id:
           maxval = perf_obj.browse(cr, uid, perf_id[0]).value 
         
        for case in self.browse(cr, uid, ids):
            res[case.id] = {'myskill_points':0.00, 'mykpi_points':0.00,
                            'skill_points':0.00, 'kpi_points':0.00, 'hr_points':0.00}
            myskpts = skpts = 0.00
            
            if case.skill_ids:
                cnt = 0
                for sk in case.skill_ids:
                    cnt += 1
                    myskpts += (sk.self_value_id and sk.self_value_id.value) or 0.00
                    skpts += (sk.man_value_id and sk.man_value_id.value) or 0.00
                    
                res[case.id]['myskill_points'] = (myskpts / ((maxval * cnt) or 1)) * 100
                res[case.id]['skill_points'] = (skpts / ((maxval * cnt) or 1)) * 100
                
            if case.kpi_current_ids:
                for kp in case.kpi_current_ids:
                    res[case.id]['mykpi_points'] += kp.self_rating
                    res[case.id]['kpi_points'] += kp.supr_rating

            if case.assess_ids:
                for h in case.assess_ids:
                    res[case.id]['hr_points'] += h.points
           
        return res    
    
    def _get_timeout(self,cr,uid,ids,name,args,context=None):
        res = {}
        for case in self.browse(cr,uid,ids):
            res[case.id] = {'emp_timeout':False, 'man_timeout':False}
            print "%%%%%%",res
            if time.strftime("%Y-%m-%d") > case.emp_end_date and case.state != 'emp_submit':
#               self.write(cr, uid, [case.id], {'state': 'emp_timeout'})
               cr.execute("update ed_appraisal set state = 'emp_timeout' where id = %d"%(case.id))
               res[case.id]['emp_timeout'] = True              
            
            if time.strftime("%Y-%m-%d") > case.man_end_date and case.state == 'emp_submit':
#               self.write(cr, uid, [case.id], {'state': 'man_timeout'})
               cr.execute("update ed_appraisal set state = 'man_timeout' where id = %d"%(case.id))
               res[case.id]['man_timeout'] = True               
        return res
        
    def _get_peer_ids(self, cr, uid, ids, field_name, arg, context=None):
        
        peersuper_obj = self.pool.get("ed.peersuper.appraisal")
        res = {}
        for case in self.browse(cr,uid,ids,context):
            res[case.id] = peersuper_obj.search(cr, uid, [('resource_id', '=',case.resource_id.id),('rate_for_id','=',case.emp_id.id),('type','=','peer'),('state','=','done')])
            
        return res
    
    def _get_supervisor_ids(self, cr, uid, ids, field_name, arg, context=None):
        
        peersuper_obj = self.pool.get("ed.peersuper.appraisal")
        res = {}
        for case in self.browse(cr,uid,ids,context):
            res[case.id] = peersuper_obj.search(cr, uid, [('resource_id', '=',case.resource_id.id),('rate_for_id','=',case.emp_id.id),('type','=','supervisor'),('state','=','done')])
            
        return res
    
    def _get_JoinDate(self,cr,uid,ids,name,args,context=None):
        res = {}
        for case in self.browse(cr,uid,ids):
            if case.emp_id:
               res[case.id] = case.emp_id.date_of_join
            else:
                res[case.id] = False                
        return res
              
         
    _columns = {
                 'start_date' : fields.date('Start Date'),
                 'end_date' : fields.date('End Date'),
                 'name' : fields.char("Description", size=100),
                 'emp_end_date' : fields.date('Employee End Date'),
                 'man_end_date' : fields.date('Manager End Date'),
                 'emp_id' : fields.many2one('hr.employee','Employee'),
                 'manager_id' : fields.many2one('hr.employee','Manager'),
                 'manager_id2':fields.many2one('hr.employee','Manager2'),
                 'manager_id3':fields.many2one('hr.employee','Manager3'),
                 'resource_id' : fields.many2one('ed.resource.appraisal','Resource Appraisal'),
                 'appraised_hr':fields.many2one('res.users','Appraised By HR'),                 
                 
                 'skill_text' : fields.text('Skills Applicable to the Department',readonly=True,states={'draft':[('readonly',False)]}),
                 'coment_text' : fields.text('Appraisers COMMENTS', readonly=True,states={'emp_submit': [('readonly', False)]}),
                 'sup_comment' : fields.text('Supervisor Comments', readonly=True,states={'emp_submit': [('readonly', False)]}),
                 'hr_comment' : fields.text('HR Comments', readonly=True,states={'man_acpt': [('readonly', False)]}),
                 
                 'initator_ids' : fields.one2many('ed.app.initiator','appraisal_id','Initiator'),
                 'skill_ids' : fields.one2many('ed.app.skills.behave','appraisal_id','Part 1'),
                 'training_ids' : fields.one2many('ed.app.training','appraisal_id','Part 3'),
                 'kpi_current_ids' : fields.one2many('ed.app.kpi.current.years','appraisal_id','Part 4'),
                 'kpi_nxt_ids' :fields.one2many('ed.app.kpi.nxt.years','appraisal_id','Part 4', readonly=True, states={'emp_submit': [('readonly', False)]}),
                 'assess_ids' : fields.one2many('ed.app.hr.assess','appraisal_id','Part 5', readonly=True, states={'man_acpt': [('readonly', False)]}),
                 'overall_ids' : fields.one2many('ed.app.overall','appraisal_id','Part 6'),
                 
                 'state' : fields.selection(EmpApp_STATES,'State'),
                 
                 'myskill_points': fields.function(_get_all_points, method = True, type="float", string='Skill Points', multi = 'pts'),
                 'mycompet_points': fields.float('Competency Points', readonly=True,states={'draft': [('readonly', False)]}),
                 'mykpi_points': fields.function(_get_all_points, method = True, type="float", string='KPI Points', multi = 'pts'),
                 'skill_points': fields.function(_get_all_points, method = True, type="float", string='Skill Points', multi = 'pts'),
                 'compet_points': fields.float('Competency Points', readonly=True,states={'emp_submit': [('readonly', False)]}),
                 'kpi_points': fields.function(_get_all_points, method = True, type="float", string='KPI Points', multi = 'pts'),
                 'hr_points': fields.function(_get_all_points, method = True, type="float", string='KPI Points', multi = 'pts'),
                 'peer_ids': fields.function(_get_peer_ids, method=True, type='one2many', obj='ed.peersuper.appraisal', string='Peer Appraisal' ,readonly=True),
                 'super_ids': fields.function(_get_supervisor_ids, method=True, type='one2many', obj='ed.peersuper.appraisal', string='Supervisor Appraisal' ,readonly=True),
                
                 'emp_timeout':fields.function(_get_timeout, method = True, type ='boolean',string="Employee Timeout"),
                 'man_timeout':fields.function(_get_timeout, method = True, type ='boolean',string="Manager Timeout"),
                 'join_date' : fields.function(_get_JoinDate, method = True, type ='date',string="Date of Joining"),              
               }  
    
    _defaults = {
                'state' :  lambda *a: 'draft',
               }
    _order = 'start_date desc'
     
    def button_submit(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'emp_submit'})
        reqst_obj = self.pool.get('res.request')
        for case in self.browse(cr,uid,ids):
            #Notification to Employee
            req_ids = []
            vals = { 
                    'name': str(case.emp_id.name) + 'Appraisal Form'
                   ,'act_to': case.emp_id.manager_id and case.emp_id.manager_id.user_id and case.emp_id.manager_id.user_id.id or False
                   ,'body':'Employee ' + str(case.emp_id.name) + ' has submitted the appraisal form for the period ' + str(case.start_date) + 
                           ' to ' + str(case.end_date) + '. \nPlease visit the ' 
                           'Team Appraisal link of the HR menu to enter your remarks.'
                   ,'priority':'2'
                    } 
            if vals['act_to']:
                req_id = reqst_obj.create(cr, uid, vals)
                req_ids.append(req_id)
            
            vals['act_to'] = case.emp_id.manager2_id and case.emp_id.manager2_id.user_id and case.emp_id.manager2_id.user_id.id or False
            if vals['act_to']:
                req_id = reqst_obj.create(cr, uid, vals)
                req_ids.append(req_id)
            
            vals['act_to'] = case.emp_id.manager3_id and case.emp_id.manager3_id.user_id and case.emp_id.manager3_id.user_id.id or False
            if vals['act_to']:
                req_id = reqst_obj.create(cr, uid, vals)
                req_ids.append(req_id)
                
            reqst_obj.request_send(cr, uid, req_ids) 
        return True
    
    def button_manAccept(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'man_acpt'})
        reqst_obj = self.pool.get('res.request')
        user_obj = self.pool.get('res.users')
        for case in self.browse(cr,uid,ids):
            #Notification to Employee
                man_name = user_obj.browse(cr,uid,uid).name
                vals = { 
                        'name': str(man_name or False) + ' has approved ' + str(case.emp_id.name) + ' Appraisal Form'
                       ,'act_to': case.emp_id.manager_id and case.emp_id.manager_id.manager_id and case.emp_id.manager_id.manager_id.user_id and case.emp_id.manager_id.manager_id.user_id.id or False
                       ,'body':'Manager ' + str(man_name or '') + ' has submitted the appraisal form of ' 
                                + str(case.emp_id.name) + ' for the period ' + str(case.start_date) + 
                               ' to ' + str(case.end_date) + '. \nPlease visit the ' 
                               'HR Appraisal link of the HR menu to enter your remarks.'
                       ,'priority':'2'
                        }
                if vals['act_to']: 
                    req_id = reqst_obj.create(cr, uid, vals)
                    reqst_obj.request_send(cr, uid, [req_id]) 
        return True 
    
    def button_manReject(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def button_hrAccept(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'hr_acpt','appraised_hr':uid})
        reqst_obj = self.pool.get('res.request')
        user_obj = self.pool.get('res.users')
        for case in self.browse(cr,uid,ids):
            #Notification to Employee
            hr_name = user_obj.browse(cr,uid,uid).name
            if case.emp_id.user_id:
                vals = { 
                        'name': str(hr_name or '') + ' has approved  your Appraisal Form'
                       ,'act_to': case.emp_id.user_id.id
                       ,'body':'Manager ' + str(hr_name or '') + ' has approved your appraisal form ' 
                                ' for the period ' + str(case.start_date) + 
                               ' to ' + str(case.end_date) + '. \nPlease visit the ' 
                               'My Appraisal link of the HR menu to see your remarks.'
                       ,'priority':'2'
                        } 
                req_id = reqst_obj.create(cr, uid, vals)
                reqst_obj.request_send(cr, uid, [req_id])
        return True
    
    def button_hrReject(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'emp_submit'})
        return True
    
    def print_report(self, cr, uid, ids, context=None):
        for case in self.browse(cr,uid,ids):
           if context is None:
               context = {}
        data = {}
        data['ids'] = ids 
        data['model'] = 'ed.appraisal'
        return {
                'report_name': 'ed.appraisal',
                'type': 'ir.actions.report.xml',
                'target': 'new',
                'datas': data,
                }
     
    
ed_appraisal() 

class ed_app_initiator(osv.osv):
    _name = 'ed.app.initiator'
    _description = "Initiator" 
    _columns  = {
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
                  'initiate_ques' : fields.char('Question',size=500),
                  'initiate_desc' : fields.text('Description', readonly=True, states={'draft': [('readonly', False)]}),
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  'name':fields.char('Name',size=5),
                 }  
#    _columns  = {
#                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
#                  'initiate_ques' : fields.char('Question',size=500),
#                  'initiate_desc' : fields.text('Description'),
#                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
#                  'name':fields.char('Name',size=5),
#                 }  
 
ed_app_initiator()  

class ed_app_skills_behave(osv.osv):
    _name = 'ed.app.skills.behave'
    _description = "Skills & Behaviour"
            
    _columns  = {
                  'name':fields.char('Name',size=5),
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
                  'p1_ques' : fields.char('Question',size=100),
                  'p1_desc' : fields.text('Description'),
                  'self_value_id': fields.many2one('ed.performance.review','Self', readonly=True,states={'draft': [('readonly', False)]}),
                  'man_value_id' : fields.many2one('ed.performance.review','Manager/Supervisor', readonly=True, states={'emp_submit': [('readonly', False)]}), 
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  
                 }
     
         
#    _columns  = {
#                  'name':fields.char('Name',size=5),
#                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
#                  'p1_ques' : fields.char('Question',size=100),
#                  'p1_desc' : fields.text('Description'),
#                  'self_value_id': fields.many2one('ed.performance.review','Self'),
#                  'man_value_id' : fields.many2one('ed.performance.review','Manager/Supervisor'), 
#                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
#                  
#                 }
ed_app_skills_behave()  


class ed_app_training(osv.osv):
    _name = 'ed.app.training'
    _description = "Training Need Analysis"
    _columns  = {
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
                  'train_ques' : fields.char('Question',size=100),
                  'train_desc' : fields.text('Description', readonly=True,states={'emp_submit': [('readonly', False)]}),                  
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  'name':fields.char('Name',size=5),
                 } 

#    _columns  = {
#                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
#                  'train_ques' : fields.char('Question',size=100),
#                  'train_desc' : fields.text('Description'),                  
#                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
#                  'name':fields.char('Name',size=5),
#                 } 
ed_app_training()  

class ed_app_kpi_current_years(osv.osv):
    _name = 'ed.app.kpi.current.years'
    _description = "KPI Review"
    
    def _default_state(self, cr, uid, context=None):
        cr.execute("""
                    select true
                    from res_groups_users_rel gu
                    inner join res_groups g on g.id = gu.gid
                    where g.name = 'ED-HR User'
                    and gu.uid = """ + str(uid) + """ 
                """)
        chk = cr.fetchone()
        if chk and chk[0]: return 'draft' 
        else: return False
        
    _columns  = {
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
                  'department_id' : fields.many2one('hr.department','Department',required=True, readonly=True,states={'draft': [('readonly', False)]}),
                  'desc_text' : fields.text('Description of Work', readonly=True,states={'draft': [('readonly', False)]}),
                  'report_to' : fields.char('Reporting To',size=100, readonly=True,states={'draft': [('readonly', False)]}),
                  'weights' : fields.float('Weights (Importance of the KPI as a %)', readonly=True,states={'draft': [('readonly', False)]}),
                  'self_rating' : fields.float('Self-rating by the Appraisee %', readonly=True,states={'draft': [('readonly', False)]}),
                  'supr_rating' : fields.float('Appraisers rating', readonly=True, states={'emp_submit': [('readonly', False)]}),
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  'name':fields.char('Name',size=5),
                 }
#    _columns  = {
#                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
#                  'department_id' : fields.many2one('hr.department','Department'),
#                  'desc_text' : fields.text('Description of Work'),
#                  'report_to' : fields.char('Reporting To',size=100),
#                  'weights' : fields.float('Weights (Importance of the KPI as a %)'),
#                  'self_rating' : fields.float('Self-rating by the Appraisee %'),
#                  'supr_rating' : fields.float('Appraisers rating'),
#                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
#                  'name':fields.char('Name',size=5),
#                 } 
    _defaults = {
                 'state': _default_state,
                 }
ed_app_kpi_current_years()  

class ed_app_kpi_nxt_years(osv.osv):
    _name = 'ed.app.kpi.nxt.years'
    _description = "KPI Settings"
    _columns  = {
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),                  
                  'department_id' : fields.many2one('hr.department', 'Department'),
                  'desc_text' : fields.text('Description of Work' ),
                  'time_line' : fields.char('Timeline for KPI',size=20),
                  'report_to' : fields.char('Reporting To',size=100),
                  'weights' : fields.float('Weights (Importance of the KPI as a %)'),
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  'name':fields.char('Name',size=5),
                 
                 } 
ed_app_kpi_nxt_years()  

class ed_app_hr_assess(osv.osv):
    _name = 'ed.app.hr.assess'
    _description = "HR Assessment"
    _columns  = {
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
                  'hr_param' : fields.char('Question',size=250),
                  'hr_outof' : fields.integer('Out Of'),
                  'points':fields.float('Points'),
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  'name':fields.char('Name',size=5),
                }
ed_app_hr_assess()  

class ed_app_overall(osv.osv):
    _name = 'ed.app.overall'
    _description = "Overall Summary"    
    
    def _get_ScorePts(self, cr, uid, ids, name, args, context=None):
        res = {} 
        EmpApp_obj = self.pool.get('ed.appraisal')
        
        for case in self.browse(cr, uid, ids):
            res[case.id] = {'point':0.00, 'score':0.00}
            pts = 0.00
            if case.eval_param == 'Skills & Behaviour' : 
                pts = case.appraisal_id and case.appraisal_id.skill_points or 0.00
                 
            elif case.eval_param == 'Competency Assessment' : 
                pts = case.appraisal_id and case.appraisal_id.compet_points or 0.00
                 
            elif case.eval_param == 'KPI' : 
                pts = case.appraisal_id and case.appraisal_id.kpi_points or 0.00
                
            elif case.eval_param == 'Human Resource Assessment': 
                pts = case.appraisal_id and case.appraisal_id.hr_points or 0.00
            print "Points",case.id,pts
            res[case.id]['point'] = pts
            res[case.id]['score'] = (pts * case.weight_age) / 100 
        return res
        
    _columns  = {
                  'appraisal_id' : fields.many2one('ed.appraisal','Appraisals'),
                  'eval_param' : fields.char('Evaluation Parameters',size=250),
                  'weight_age' : fields.float('Weight-age'),
                  'point' : fields.function(_get_ScorePts, method=True, type='float', string='Point(on 100)', multi="pts" ,store=True),
                  'score' : fields.function(_get_ScorePts, method=True, type='float', string='Score', multi="pts" ,store=True),
                  'state' : fields.related('appraisal_id', 'state', type='selection', selection=EmpApp_STATES, string='Parent State'),
                  'name':fields.char('Name',size=5),
                }
ed_app_overall()  


class ed_hr_tasks(osv.osv):
    _name = 'ed.hr.tasks'
    _description = "Employee Tasks"
    
    def get_employee_id(self, cr, uid, ids, *args):  
        res = {}       
        cr.execute("select h.id from hr_employee h \
                    inner join resource_resource r on r.id = h.resource_id \
                    where r.user_id = %d"%(uid))  
        res = cr.fetchone()
        return res and res[0] or False
      
    
    _columns  = {
                    'employee_id' : fields.many2one('hr.employee','Employee'),
                    'to_do_date' : fields.datetime('Date'),
                    'status_id' : fields.many2one('ed.hr.status','Status'),
                    'work_desc' : fields.text('Work Description')
                 }
    _order = 'to_do_date desc'
    _defaults ={
                'employee_id' : get_employee_id                
                }
ed_hr_tasks()    

class ed_peersuper_appraisal(osv.osv):
    _name='ed.peersuper.appraisal'
    
    def _get_avg_score(self,cr,uid,ids,name,args,context=None):
        res = {}        
        for case in self.browse(cr,uid,ids):
             score = 0.00 
             count = 0    
             if case.line_id:
                 for ln in case.line_id:
                     score += ln.rating
                     count += 1
             res[case.id] = score/(count or 1)
                                       
        return res
        
    
    _columns={'rate_by_id':fields.many2one('hr.employee','Rated By',readonly=True),
              'rate_for_id':fields.many2one('hr.employee','Rated For',readonly=True),
              'resource_id' : fields.many2one('ed.resource.appraisal','Appraisal',readonly=True),
              'type':fields.selection([('peer','Peer'),('supervisor','Supervisor')],'Type',readonly=True),
              'line_id':fields.one2many('ed.peersuper.appraisal.line','peersuper_id','Parent',readonly=True,states={'draft': [('readonly', False)]}),
              'comments':fields.text('Comments',readonly=True,states={'draft': [('readonly', False)]}),
              'sugg':fields.text('Suggestions',readonly=True,states={'draft': [('readonly', False)]}),
              'state' : fields.selection(EmpApp_STATES,'State',readonly=True),
              'score': fields.function(_get_avg_score, method=True, string='Score', type='float'),
              }
#    _columns={'rate_by_id':fields.many2one('hr.employee','Rated By',readonly=True),
#              'rate_for_id':fields.many2one('hr.employee','Rated For',readonly=True),
#              'resource_id' : fields.many2one('ed.resource.appraisal','Appraisal',readonly=True),
#              'type':fields.selection([('peer','Peer'),('supervisor','Supervisor')],'Type',readonly=True),
#              'line_id':fields.one2many('ed.peersuper.appraisal.line','peersuper_id','Parent',readonly=True),
#              'comments':fields.text('Comments',readonly=True,states={'draft': [('readonly', False)]}),
#              'sugg':fields.text('Suggestions',readonly=True,states={'draft': [('readonly', False)]}),
#              'state' : fields.selection(EmpApp_STATES,'State',readonly=True),
#              'score': fields.function(_get_avg_score, method=True, string='Score', type='float'),
#              }
    _defaults={'state':'draft'}
ed_peersuper_appraisal()

class ed_peersuper_appraisal_line(osv.osv):
    _name='ed.peersuper.appraisal.line'
    _columns={'psparameters_id':fields.many2one('ed.peersuper.parameters','Peer Parameters',readonly=True),              
              'rating':fields.selection(POINTS,'Points'),   
              'peersuper_id':fields.many2one('ed.peersuper.appraisal','Peer Supervisor Line')           
              }
    
    
    
ed_peersuper_appraisal_line()                


class hr_department(osv.osv):
    _inherit = 'hr.department'
    _columns = {
                'work_ids':fields.one2many('ed.company.work.time','depat_id','Work Timings')
               }
    
    
    def write(self, cr, uid, ids,vals,context=None): 
        emp_obj = self.pool.get('hr.employee')
        res = super(hr_department, self).write(cr, uid, ids, vals,context)
        for case in self.browse(cr,uid,ids):
            if 'work_ids' in vals:
                emp_ids = emp_obj.search(cr,uid,[('department_id','=',case.id)])
                emp_obj.update_worktimings( cr, uid, emp_ids,case.id,context)
        return res
    
hr_department()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {'ctc':fields.integer('CTC'),
                }
hr_contract()

class ed_hr_news(osv.osv):
    _name = 'ed.hr.news'
    _description = "News"
    _columns = {
                   
                'news_desc' :fields.char('Description',size=500),
                'news_date' :fields.date('Date')
                }
    _order = 'news_date'

ed_hr_news()   

class hr_job(osv.osv):
    _inherit = 'hr.job'
    _columns = {
                'job_level':fields.char('Level',size=50),
                }
hr_job() 

class ed_hr_allocation(osv.osv):
    _name = "ed.hr.allocation"
    _description = "Allocation"
    _columns = {
                 'hr_emp_id' : fields.many2one('hr.employee','Employee Details',ondelete = 'cascade'),
                 'department_id':fields.many2one('hr.department','Department'),
                 'allocation' : fields.float('Allocation')
                 
                
                }
ed_hr_allocation()