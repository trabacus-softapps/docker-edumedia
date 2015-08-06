from openerp.osv import fields,osv
from openerp.tools.translate import _
import config 


def get_default_Partnermap(self, cr, uid, context=None):
    
    partner_obj = self.pool.get('res.partner')
    ed_type = context and context.get('search_default_ed_type',False)
    ed_type1 = context and context.get('mon_edtype',False)
    city = context and context.get('mon_city',False)
    maps = {'activity':'ed_sh_act', 'akshaya':'ed_sh_aksh' }
    partner_ids = '0'
    if ed_type:
        partner_ids = partner_obj.search(cr, uid, [(maps[ed_type],'=',True)])
    elif city:
        partner_ids = partner_obj.search(cr, uid, [(maps[ed_type1],'=',True),('ed_city_id','=',city)])
    val = '0'
    if partner_ids:
       for p in partner_ids:
            val = val + str(p) + ","
       val = val[0:(len(val) - 1)]
        
    return val

class time_table(osv.osv):
    _name='time.table' 
    
    def _get_default_city(self, cr, uid, context=None):  
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.city_id.id or False
    
    _columns={
              'account_id':fields.many2one('account.fiscalyear','Financial Year',required=True),
              'city_id':fields.many2one('ed.city','City'),
              'month_id':fields.one2many('ed.auto.month','table_id','Months'),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
            }
    _defaults={
               'city_id':_get_default_city
               }
    
    def name_get(self, cr, uid, ids, context=None):
        result= []
        if not all(ids):
            return result
        for case in self.browse(cr, uid, ids, context=context):
            name = case.id
            result.append((case.id,name))
        return result
    
    

        
    def create(self, cr, uid, vals, context=None):
        time_id = False
        class_obj = self.pool.get('ed.auto.month')
        month_list={1:'m1',2:'m2',3:'m3',4:'m4',5:'m5',6:'m6',7:'m7',8:'m8',9:'m9',10:'m10',11:'m11',12:'m12',}          
        time_id = super(time_table, self).create(cr, uid, vals, context)
        
        for i in range(1,13):
            class_obj.create(cr,uid,{'table_id' : time_id,
                                 'name' : month_list.get(i),
                                 'ed_type1':vals['ed_type']
                                 })       
        return time_id
        
    
time_table()

class ed_auto_month(osv.osv):
    
    _name='ed.auto.month'    
    _columns={'table_id':fields.many2one('time.table','month'), 
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
              'time_line':fields.one2many('time.table.lines','month_id','Time Table'),
              'ed_type1':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              'state':fields.selection((['draft','Draft'],['publish','Publish'],['cancel','Cancel']),'State',readonly=True),
             }
    
    _defaults = {'state':'draft',
                 }
     
    def confirm_form(self,cr,uid,ids,context=None):
        
        session_obj = self.pool.get('ed.activity.session')
        table_obj = self.pool.get('time.table')
        tableln_obj = self.pool.get('time.table.lines')
        city_obj = self.pool.get('ed.city')
        session_id = 0
        for case in self.browse(cr,uid,ids):
            city_id = table_obj.browse(cr, uid,case.table_id.id).city_id.id
            for time_ln in case.time_line:
                if time_ln.session_id:
                    status = session_obj.browse(cr,uid,time_ln.session_id).status_id.name
                    if status != 'Completed':
                        #to write in existing records of sessions
                        session_obj.write(cr,uid,time_ln.session_id,{'ed_date':time_ln.ed_date,
                                                                        'day_id':time_ln.day_id.id,
                                                                        'time_from':time_ln.time_from,
                                                                        'time_to':time_ln.time_to,
                                                                        'partner_id':time_ln.partner_id.id,
                                                                        'ed_class':time_ln.ed_class,
                                                                        'ed_sec':time_ln.ed_sec,
                                                                        'content_id':time_ln.content_id.id,
                                                                        'topic_id':time_ln.topic_id.id,
                                                                        'user_id':time_ln.user_id.id,
                                                                        'ed_type':time_ln.ed_type,
                                                                        })
                        #to create new records
                else:
                    session_id =  session_obj.create(cr,uid,{'city_id':city_id,
                                                'ed_date':time_ln.ed_date,
                                                'day_id':time_ln.day_id.id,
                                                'time_from':time_ln.time_from,
                                                'time_to':time_ln.time_to,
                                                'partner_id':time_ln.partner_id.id,
                                                'ed_class':time_ln.ed_class,
                                                'ed_sec':time_ln.ed_sec,
                                                'content_id':time_ln.content_id.id,
                                                'topic_id':time_ln.topic_id.id,
                                                'user_id':time_ln.user_id.id,
                                                'ed_type':time_ln.ed_type,
                                                #'user_id':uid
                                                })
                    tableln_obj.write(cr,uid,[time_ln.id],{'session_id':session_id})
        self.write(cr, uid, ids, {'state': 'publish'})
        return True  
        
    def cancel_form(self,cr,uid,ids,context=None):        
        self.write(cr, uid, ids, {'state': 'draft'})
        
        return True
        
       
    
ed_auto_month()


class time_table_lines(osv.osv):
    _name="time.table.lines"
    
#    def _get_default_user(self, cr, uid, context=None):        
#        if context and context.get('portal', False):
#            return False
#        return uid
    
    def _get_default_edType(self, cr, uid, context=None): 
        return context and context.get('mon_edtype', False)
        
    
    def _get_mapping_id(self, cr, uid,ids,fieldnames, args, context=None):
        res = {}  
        val = ""       
        user_ids = []
        uid_city = self.pool.get('res.users').browse(cr,uid,uid)
        saletm_id = self.pool.get('crm.case.section').search(cr,uid,[('name','=','Activity Department')])[0]
        for case in self.browse(cr,uid,ids):    
            if case.city_id:
                city = case.city_id.id
            else:
                city = uid_city.city_id and uid_city_id.id or False                
            
            cr.execute("select id from res_users where context_section_id = %d and city_id = %d" %(saletm_id,city))             
            user_ids = cr.fetchall()
            for s in user_ids:
                 val = val + str(s[0]) + ","
            val = val[0:(len(val) - 1)] 
            res[case.id] = val     
            return res
    
    
    def _get_partner_ids(self, cr, uid,ids,fieldnames, args, context=None):
        
        res = {}      
        val = ""
        for case in self.browse(cr,uid,ids):
            context.update({'search_default_ed_type':case.ed_type})
            val = get_default_Partnermap(self, cr, uid, context=context)
            res[case.id] = val
        return res
    
    _columns={'month_id':fields.many2one('ed.auto.month','Table_lines'),
              'ed_date':fields.date('Date'),
              'day_id':fields.many2one('ed.day','Day'),
#              'partner_mapping': fields.char('Partner Mapping', size=128), 
              'partner_mapping': fields.function(_get_partner_ids, method=True, string='Partner Mapping', type='text'),
              'partner_id':fields.many2one('res.partner','School', domain="[('id', 'in', [int(s) for s in partner_mapping.split(',')])]"),
#               'time_from':fields.time('Time From'),
#               'time_to':fields.time('Time To'),
              'time_from':fields.datetime('Time From'),
              'time_to':fields.datetime('Time To'),
              'session_id':fields.integer('Sessions'),
              'ed_class':fields.selection(config.CLASS_STD,'STD'),
              'ed_sec':fields.char('Section',size=50),
              'content_id':fields.many2one('ed.content','Content'),
              'topic_id':fields.many2one('ed.topic','Topic'),
              'uid_mapping': fields.function(_get_mapping_id, method=True, string='UID Mapping', type='char', size=128),
              'user_id' : fields.many2one('res.users','Facilitator', domain="[('id', 'in', [int(s) for s in uid_mapping.split(',')])]"),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              }
    
    _defaults={
#               'user_id':_get_default_user,
               'ed_type':_get_default_edType,
               'partner_mapping':get_default_Partnermap
               }
    def write(self, cr, uid, ids,vals,context=None): 
        session_obj = self.pool.get('ed.activity.session') 
        for case in self.browse(cr, uid, ids):
             
            if 'session_id' in vals and vals['session_id']:
                status = session_obj.browse(cr,uid,vals['session_id']).status_id.name
                if status != 'covered':
                    result = super(time_table_lines, self).write(cr, uid, ids, vals, context=context)
                    return result
        return True
    
time_table_lines()

class ed_activity_session(osv.osv):
    _name='ed.activity.session'
     
    def _get_default_user(self, cr, uid, context=None):
        
        if context and context.get('portal', False):
            return False
        return uid

    def _get_default_city(self, cr, uid, context=None):  
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.city_id.id or False
        
    def _get_mapping_id(self, cr, uid,ids,fieldnames, args, context=None):
        res = {}  
        val = ""       
        user_ids = []
        uid_city = self.pool.get('res.users').browse(cr,uid,uid)
        saletm_id = self.pool.get('crm.case.section').search(cr,uid,[('name','=','Activity Department')])[0]
        for case in self.browse(cr,uid,ids):    
            if case.city_id:
                city = case.city_id.id
            else:
                city = uid_city.city_id and uid_city_id.id or False
                
            
            cr.execute("select id from res_users where context_section_id = %d and city_id = %d" %(saletm_id,city))             
            user_ids = cr.fetchall()
            for s in user_ids:
                 val = val + str(s[0]) + ","
            val = val[0:(len(val) - 1)] 
            res[case.id] = val     
            return res  
     
    def _get_partner_ids(self, cr, uid,ids,fieldnames, args, context=None):
        
        res = {}      
        val = ""
        for case in self.browse(cr,uid,ids):
            context.update({'search_default_ed_type':case.ed_type})
            val = get_default_Partnermap(self, cr, uid, context=context)
            res[case.id] = val
        return res
        

    _columns={'city_id':fields.many2one('ed.city','City'), 
              'ed_date':fields.date('Date'),
              'day_id':fields.many2one('ed.day','Day'),
#               'time_from':fields.time('Time From'),
#               'time_to':fields.time('Time To'),
              'time_from':fields.datetime('Time From'),
              'time_to':fields.datetime('Time To'),
              'partner_mapping': fields.function(_get_partner_ids, method=True, string='Partner Mapping', type='text'), 
              'partner_id':fields.many2one('res.partner','School', domain="[('id', 'in', [int(s) for s in partner_mapping.split(',')])]"),
              'ed_class':fields.selection(config.CLASS_STD,'STD'),
              'ed_sec':fields.char('Section',size=50),
              'content_id':fields.many2one('ed.content','Content'),
              'topic_id':fields.many2one('ed.topic','Topic'),
              'ed_total':fields.integer('Students'),
              'method_ids':fields.many2many('ed.method.used','method_sessions_rel','method_id','session_id','Methodology Used'),
              'sess_count':fields.integer('No .of Sessions'),
              'stu_reaction':fields.text('students Reaction'),
              'otr_act':fields.text('Other Activites'),
              'observ':fields.text('Facilitator Observation'),
              'train_req':fields.text('Training Requirement'),
              'status_id':fields.many2one('ed.status','Status'),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              'uid_mapping': fields.function(_get_mapping_id, method=True, string='UID Mapping', type='char', size=128), 
              'user_id' : fields.many2one('res.users','Facilitator', domain="[('id', 'in', [int(s) for s in uid_mapping.split(',')])]"),
        
              
              }
    _defaults={  
               'city_id':_get_default_city,
               'user_id':_get_default_user,
               'partner_mapping':get_default_Partnermap
          
               }
    _order = 'ed_date desc,ed_class'
    
    def onchange_city(self, cr, uid, ids, city):
        res = {}
        user_ids = []
        val = ''
        saletm_id = self.pool.get('crm.case.section').search(cr,uid,[('name','=','Activity Department')])[0]
        cr.execute("select id,name from res_users where context_section_id = %d and city_id =%d" %(saletm_id,city))             
        user_ids = cr.fetchall()
        for s in user_ids:
             val = val + str(s[0]) + ","
        val = val[0:(len(val) - 1)] 
        res['uid_mapping'] = val
        return {'value':res}
    
ed_activity_session()


class ed_talent(osv.osv):
    _name='ed.talent'
    
    def _get_partner_ids(self, cr, uid,ids,fieldnames, args, context=None):
        
        res = {}      
        val = ""
        for case in self.browse(cr,uid,ids):
            context.update({'search_default_ed_type':case.ed_type})
            val = get_default_Partnermap(self, cr, uid, context=context)
            res[case.id] = val
        return res

    _columns={
#              'partner_mapping': fields.char('Partner Mapping', size=128), 
              'partner_mapping': fields.function(_get_partner_ids, method=True, string='Partner Mapping', type='text'),
              'partner_id':fields.many2one('res.partner','School', domain="[('id', 'in', [int(s) for s in partner_mapping.split(',')])]"),
              'prize_id':fields.one2many('ed.prize','talent_id','Prize List'),
              'ed_date':fields.date('Date'),
              'event_name':fields.char('Events Name',size=500),
              'event_topic':fields.char('Events Topic',size=500),
              'ed_total':fields.integer('No. Of Students'),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              }
    _defaults={'partner_mapping':get_default_Partnermap}
ed_talent()

class ed_prize(osv.osv):
    _name='ed.prize'
    _columns={
              'talent_id':fields.many2one('ed.talent','Talent'),
              'name':fields.char('Name of the Competitions',size=500,required=True),
              'first':fields.char('First Prize',size=200),
              'ed_class1':fields.selection(config.CLASS_STD,'Std'),
              'ed_sec1':fields.selection(config.SECTION,'Section'),
              'second':fields.char('Second Prize',size=200),
              'ed_class2':fields.selection(config.CLASS_STD,'Std'),
              'ed_sec2':fields.selection(config.SECTION,'Section'),
              'third':fields.char('Third Prize',size=200),
              'ed_class3':fields.selection(config.CLASS_STD,'Std'),
              'ed_sec3':fields.selection(config.SECTION,'Section'),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),
              }
ed_prize()



class ed_student_data(osv.osv):
    _name='ed.student.data'    
    
    def _get_partner_ids(self, cr, uid,ids,fieldnames, args, context=None):
        
        res = {}      
        val = ""
        for case in self.browse(cr,uid,ids):
            context.update({'search_default_ed_type':case.ed_type})
            val = get_default_Partnermap(self, cr, uid, context=context)
            res[case.id] = val
        return res
    
    _columns={
              'name':fields.char('Name',size=500),
#              'partner_mapping': fields.char('Partner Mapping', size=128), 
              'partner_mapping': fields.function(_get_partner_ids, method=True, string='Partner Mapping', type='text'),
              'partner_id':fields.many2one('res.partner','School', domain="[('id', 'in', [int(s) for s in partner_mapping.split(',')])]"),
              'ed_class':fields.selection(config.CLASS_STD,'Class'),
              'ed_sec':fields.char('Section',size=20),
              'contact':fields.char('Contact No',size=100),
              'e_mail':fields.char('E-Mail',size=200),
              'address':fields.char('Permanent Address',size=500),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),                 
              }
    _defaults={'partner_mapping':get_default_Partnermap}
    
ed_student_data()


class ed_cce(osv.osv):
    _name='ed.cce'
    
    def _get_all_totalscore(self, cr, uid, ids, field_name, arg, context):
        
         res = {}
         t_total = s_total = e_total = v_total = a_total = total = percentage = 0.00
         grade_id = 0
         grade = ''
         subtotal = 250
         for case in self.browse(cr, uid, ids):
            res[case.id] = {'total':0}
            if case.film_score_ids:
                for ln in case.film_score_ids:
                    t_total += ln.think_skills
                    s_total += ln.social_skills
                    e_total += ln.emot_skills
                    v_total += ln.values
                    a_total += ln.attitude
                    if t_total > 50:
                       raise osv.except_osv(_('Warning'), _('Thinking Skills Total Score should be less than or equal to 50 !!!!'))
                    if s_total > 50:
                       raise osv.except_osv(_('Warning'), _('Social Skills Total Score should be less than or equal to 50 !!!!'))
                    if e_total > 50:
                       raise osv.except_osv(_('Warning'), _('Emotional Skills Total Score should be less than or equal to 50 !!!!'))
                    if v_total > 50:
                       raise osv.except_osv(_('Warning'), _('Values Total Score should be less than or equal to 50 !!!!'))
                    if a_total > 50:
                       raise osv.except_osv(_('Warning'), _('Attitude Total Score should be less than or equal to 50 !!!!'))
                    total += ln.think_skills + ln.social_skills + ln.emot_skills + ln.values + ln.attitude
            percentage = (total / subtotal ) * 100
            grade_id = self.pool.get('ed.grade').search(cr,uid,[('percent_from','<=',percentage),('percent_to','>=',percentage)],limit = 1)
            
            if grade_id:
                grade = self.pool.get('ed.grade').browse(cr,uid,grade_id[0]).name
          
                
            res[case.id]['total'] = total
            res[case.id]['percentage']=percentage
            res[case.id]['grade']= grade
         return res        
            
            
    def _get_partner_ids(self, cr, uid,ids,fieldnames, args, context=None):
        
        res = {}      
        val = ""
        for case in self.browse(cr,uid,ids):
            context.update({'search_default_ed_type':case.ed_type})
            val = get_default_Partnermap(self, cr, uid, context=context)
            res[case.id] = val
        return res
            
        
    _columns={
              'academic_year' : fields.many2one('account.fiscalyear','Academic Year'),
#              'partner_mapping': fields.char('Partner Mapping', size=128), 
              'partner_mapping': fields.function(_get_partner_ids, method=True, string='Partner Mapping', type='text'),
              'partner_id':fields.many2one('res.partner','School', domain="[('id', 'in', [int(s) for s in partner_mapping.split(',')])]"),
              'name' : fields.char('Student Name',size=50),
              'ed_class':fields.selection([(6,'6'),(7,'7'),(8,'8')],'STD'), 
              'ed_sec':fields.selection(config.SECTION,'Section'),  
              'film_score_ids':fields.one2many('ed.film.score','cce_id','Film Score', ondelete='cascade'), 
              'total'   : fields.function(_get_all_totalscore, readonly=True, method=True, store= True ,type='integer', string='Formative Total', multi="score"),
              'percentage'   : fields.function(_get_all_totalscore, readonly=True, method=True, store= True ,type='float', string='Formative Percentage', multi="score"),
              'grade'   : fields.function(_get_all_totalscore, readonly=True, method=True, store= True ,type='char',size=10, string='Grade', multi="score"),
              'ed_type':fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Type'),           
              }
    _defaults={'partner_mapping':get_default_Partnermap}
    
ed_cce()

class ed_film_score(osv.osv):
    _name='ed.film.score'
    
    def _get_default_edclass(self, cr, uid, context=None): 
        return context and context.get('class', False)
    
    _columns={
              'cce_id':fields.many2one('ed.cce','CCE',ondelete='cascade'),
              'think_skills':fields.integer('Thinking Skills'),
              'social_skills':fields.integer('Social Skills'),
              'emot_skills':fields.integer('Emotional Skills'),
              'values':fields.integer('Values'),
              'attitude':fields.integer('Attitude'),
              'remarks':fields.char('Remarks',size=64),
              'f_class':fields.selection(config.CLASS_STD,'STD'), 
              'film_id':fields.many2one('ed.film','Film'),
              }
    
    _defaults={
               'f_class':_get_default_edclass}
    _sql_constraints = [
        ('tskills', 'CHECK (think_skills<=50)',  'Please Enter Thinking Skills Less than or equal to 50....!!!'),
        ('sskills', 'CHECK (social_skills<=50)',  'Please Enter Social Skills Less than or equal to 50....!!!'),
        ('eskills', 'CHECK (emot_skills<=50)',  'Please Enter Emotional Skills Less than or equal to 50....!!!'),
        ('vvalues', 'CHECK (values<=50)',  'Please Enter Values Less than or equal to 50....!!!'),
        ('aattitude', 'CHECK (attitude<=50)',  'Please Enter Attitude Less than or equal to 50....!!!'),]


ed_film_score()

class ed_wrkshop_civic_awareness(osv.osv):
    _name = 'ed.wrkshop.civic.awareness'
    
    def _get_default_user(self, cr, uid, context=None):
        
        if context and context.get('portal', False):
            return False
        return uid
    _columns = {
                'city_id':fields.many2one('ed.city','City'), 
                'ed_date':fields.date('Date'),
                'day_id':fields.many2one('ed.day','Day'),
                'partner_id':fields.many2one('res.partner','School'),
                'ed_partcipants'  :fields.selection([('parents','Parents'),('teachers','Teachers'),('students','Students'),('others','Others')],'Partcipants'),
                'ed_topic' : fields.char('Topic',size=200),
                'no_of_participants' : fields.integer('No of Participants'),
                'user_id' : fields.many2one('res.users','Facilitator'),
                'ed_type':fields.selection([('workshop','Workshop'),('civic_awareness','Civic Awareness')],'Type'),
                'remarks' : fields.text('Remarks')
               }
    _defaults={
               'user_id':_get_default_user,}
ed_wrkshop_civic_awareness()              
  
           