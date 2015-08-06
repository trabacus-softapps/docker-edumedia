from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.tools
from openerp.osv.orm import except_orm, browse_record

CLASS_STD = [
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
 
MONTH=[
       (1,'January'), 
       (2,'February'), 
       (3,'March'), 
       (4,'April'), 
       (5,'May'), 
       (6,'June'),
       (7,'July'), 
       (8,'August'), 
       (9,'September'), 
       (10,'October'), 
       (11,'November'), 
       (12,'December')] 

SECTION = [ 
    ('A','A'),
    ('B','B'),
    ('C','C'),
    ('D','D'),
    ('E','E'),
    ('F','F'),
    ('G','G'),
    ('H','H'),
    ('I','I'),
    ('J','J'),
    ('K','K'),
    ('L','L'),
    ('M','M'),
    ('N','N'),
    ('O','O'),
    ('P','P'),
    ('Q','Q'),
    ('R','R'),
    ('S','S'),
    ('T','T'),
    ('U','U'),
    ('V','V'),
    ('W','W'),
    ('X','X'),
    ('Y','Y'),
    ('Z','Z'),
   
]

WEEK_NO = [
    ('w1','Week 1'),
    ('w2','Week 2'),
    ('w3','Week 3'),
    ('w4','Week 4'),
    ('w5','Week 5'),
    ('w6','Week 6'),
    ('w7','Week 7'),
    ('w8','Week 8'),
    ('w9','Week 9'),
    ('w10','Week 10'),
    ('w11','Week 11'),
    ('w12','Week 12'),
    ('w13','Week 13'),
    ('w14','Week 14'),
    ('w15','Week 15'),
    ('w16','Week 16'),
    ('w17','Week 17'),
    ('w18','Week 18'),
    ('w19','Week 19'),
    ('w20','Week 20'),
    ('w21','Week 21'),
    ('w22','Week 22'),
    ('w23','Week 23'),
    ('w24','Week 24'),
    ('w25','Week 25'),
    ('w26','Week 26'),
    ('w27','Week 27'),
    ('w28','Week 28'),
    ('w29','Week 29'),
    ('w30','Week 30'),
    ('w31','Week 31'),
    ('w32','Week 32'),
    ('w33','Week 33'),
    ('w34','Week 34'),
    ('w35','Week 35'),
    ('w36','Week 36'),
    ('w37','Week 37'),
    ('w38','Week 38'),
    ('w39','Week 39'),
    ('w40','Week 40'),
    ('w41','Week 41'),
    ('w42','Week 42'),
    ('w43','Week 43'),
    ('w44','Week 44'),
    ('w45','Week 45'),
    ('w46','Week 46'),
    ('w47','Week 47'),
    ('w48','Week 48'),
    ('w49','Week 49'),
    ('w50','Week 50'),
    ('w51','Week 51'),
    ('w52','Week 52'),
    ]

POINTS = [
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
    (11,'11'),
    (12,'12'),
    (13,'13'),
    (14,'14'),
    (15,'15'),
    (16,'16'),
    (17,'17'),
    (18,'18'),
    (19,'19'),
    (20,'20'),
    (21,'21'),
    (22,'22'),
    (23,'23'),
    (24,'24'),
    (25,'25'),    
]
class ed_board(osv.osv):
    _name='ed.board'
    _columns={
              'name':fields.char('Education Board',size=100)
              }
ed_board()

class ed_type1(osv.osv):
    _name='ed.type1'
    _columns={
              'name':fields.char('Event Type',size=100)
              }    
ed_type1()

class ed_events(osv.osv):
    _name='ed.events'
    _columns={
              'partner_id':fields.many2one('res.partner','Partner'),              
              'ed_type':fields.many2one('ed.type1','Type'),
              'ed_descp':fields.char('Description',size=100),
              'ed_evnt_dt':fields.date('Event Date'),              
              }
ed_events()

class ed_infrastucture(osv.osv):
    _name='ed.infrastucture'
    _columns={
              'name':fields.char('Infrastucture Type',size=100)
              }
    
ed_infrastucture()

class ed_moral_edu(osv.osv):
    _name='ed.moral.edu'
    _columns={
              'name':fields.char(' moral Education Type',size=100)
              }
ed_moral_edu()

class ed_designation(osv.osv):
    _name='ed.designation'
    _columns={               
              'name':fields.char('Designation Type',size=100),         
              }
    
ed_designation()

class ed_type(osv.osv):
    _name='ed.type'    
    _columns={
              'name':fields.char('School Type',size=100)
              }
ed_type()

#class details for res partner
class ed_class_details(osv.osv):
    _name='ed.class.details'        
    _columns={
              'partner_id':fields.many2one('res.partner','Partner class',readonly=True),
              'sale_id' : fields.many2one('sale.order','Sale'),
              'ed_class':fields.selection(CLASS_STD,'Class',required=True),
              'ed_sec':fields.integer('No.Of.Sections', required = True),
              'ed_students':fields.integer('No.Of.Students',required = True),
              'ed_boys':fields.integer('No.Of.Boys',required = True),
              'ed_girls':fields.integer('No.Of.Girls',required = True),
              'wrk_bk_rate':fields.integer('Work Book Rate'),
              'films_rate':fields.integer('Films Rate'),
              'rate' : fields.integer('Rate',readonly=True),
#              'ed_sc':fields.integer('SC'),
#              'ed_st':fields.integer('ST'),
#              'ed_obc':fields.integer('OBC'),
#              'ed_gm':fields.integer('GM'),
              'ed_total':fields.integer('Total')
             }
    _order='ed_class'
    
    def onchange_rate(self, cr, uid, ids, wrk_bk_rate, films_rate):
        result = {}
        total = 0
        total = wrk_bk_rate + films_rate
        result['value'] = {'rate': total}
        return result
    
    def create(self, cr, uid, vals, context=None):  
        
        if vals['ed_boys'] + vals['ed_girls'] > vals['ed_students']:
            raise osv.except_osv(_('Warning'),_("No.Of.Students is less than No.Of.Boys+No.Of.girls"))
        vals['partner_id'] = context.get('partner_id',False)
        result = super(ed_class_details, self).create(cr, uid, vals, context=context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
        
       if vals['ed_boys'] + vals['ed_girls'] > vals['ed_students']:
                raise osv.except_osv(_('Warning'),_("No.Of.Students is less than No.Of.Boys+No.Of.girls"))
       if 'wrk_bk_rate' in vals and 'films_rate' in vals:
           rate = self.onchange_rate(cr, uid, ids, vals['wrk_bk_rate'], vals['films_rate'])
           vals['rate'] = rate['value']['rate']
       res = super(ed_class_details, self).write(cr, uid, ids, vals, context=context)
       return res 
    
ed_class_details()



class ed_per(osv.osv):
    _name='ed.per'
    _columns={
              'name':fields.char('PER',size=100, required=True)
              }
ed_per()

class ed_service(osv.osv):
    _name="ed.service"
    _columns={
              'serv_id':fields.many2one('product.product','prod_serv'),
              'sale_id':fields.many2one('sale.order','Sale Order'),
              'name':fields.char('Description',size=200)
              }
ed_service()

class ed_city(osv.osv):
    _name='ed.city'
    _columns={
              'state_id':fields.many2one('res.country.state','State'),
              'name':fields.char('City',size=50),
              'code':fields.char('Code',size=5),
              }
ed_city()

class ed_training_grid(osv.osv):
    _name='ed.training.grid'
    _columns={ 
               'sale_id':fields.many2one('sale.order'),
               'user_id':fields.many2one('res.users','Assigned To'),
               'name':fields.char('Description',size=300,required=True),
               'ed_stat':fields.char('Mode',size=300),
               'sch_date':fields.date('Schedule Date',required=True),
               'complt_date' : fields.date('Completed On'),
               'ed_complt':fields.selection([('no','NO'),('yes','Yes')],'Completed?',required=True),
               }
    
    _defaults={
               'ed_complt':'no'
              }
ed_training_grid()

class ed_month(osv.osv):
    _name='ed.month'
    _description='Month'
    _columns={
              'name':fields.char('Month',size=50)
              }
ed_month()

class no_of_sessions(osv.osv):
    _name='no.of.sessions'
    _columns={
              'name':fields.integer('No.Of.Sessions')
              }
no_of_sessions()

class ed_sessions(osv.osv):
    _name='ed.sessions'
    _columns={
              'session_ids':fields.one2many('ed.class.sessions','sesion_id','sessions'),
              'ed_school':fields.char('school',size=100,readonly=True),
              'ed_so':fields.char('Sale Order',size=50,readonly=True),
              'sale_id':fields.integer('Sale id')              
              }
ed_sessions()

class ed_type_session(osv.osv):
    _name='ed.type.session'
    _columns={
              'name':fields.char('Session Type',size=100),
              }
ed_type_session()

class ed_class_sessions(osv.osv):
    _name='ed.class.sessions'
    _columns={
              'sesion_id':fields.many2one('ed.sessions','sessions'),
              'type':fields.many2one('ed.type.session','Session Type',required=True),
              'ed_class':fields.selection(CLASS_STD,'Class'),
              'month_id':fields.many2one('ed.month','Month'),
              'ed_no_seion':fields.many2one('no.of.sessions','No.OF.Session'),
              }
ed_class_sessions()

class ed_payment_type(osv.osv):
    _name='ed.payment.type'    
    _columns={
              'name':fields.char('Payment Term',size=300)
              }
ed_payment_type()

class ed_payment(osv.osv):
    _name='ed.payment'
    _columns={
              'sale_id':fields.many2one('sale.order','Payment'),
              'payment_type':fields.many2one('ed.payment.type','Payment Type'),
              'ed_amt':fields.float('Amount'),
              'ed_dd':fields.integer('DD/Cheque No.'),
              'ed_date':fields.date('Date'),
              'ed_bank':fields.char('Bank',size=300),
              }    
ed_payment()


class ed_ticket_status(osv.osv):
    _name='ed.ticket.status'
    _columns={
              'name':fields.char('Ticket Status',size=100)
              }
ed_ticket_status()

class ed_feedback(osv.osv):
    _name='ed.feedback'
    _columns={
              'sale_id':fields.many2one('sale.order','Feedback'),
              'school':fields.char('School & Class',size=100),
              'participant':fields.integer('Total No. Of Participants'),
              'film_name':fields.char('Film Name',size=100),
              'facilitator':fields.char('Facilitator',size=100),
              'feedback_ids':fields.one2many('ed.rating.film','rating_id','Rating'),
              'qutn1':fields.text('Qutn1'),
              'qutn2':fields.text('Qutn2'),
              'qutn3':fields.text('Qutn3'),
              'qutn4':fields.text('Qutn4'),
              'qutn5':fields.text('Qutn5'),
              'qutn6':fields.text('Qutn6'),
              'qutn7':fields.selection((['yes','YES'],['no','NO']),'Qutn7'),
              'qutn8':fields.text('Qutn8'),
              'qutn9':fields.text('Qutn9'),
              'qutn10':fields.text('Qutn10'),
              }
ed_feedback()

class ed_rating_film(osv.osv):
    _name='ed.rating.film'
    _columns={
              'rating_id':fields.many2one('ed.feedback','FeedBack'),
              'ed_rating':fields.selection((['poor','Poor'],['avg','Average'],['good','Good']),'Rating'),
              'ed_story':fields.selection((['five','10%  OR  5/50students'],['ten','20%  OR 10/50students'],['thirty','70%  OR 35/50students']),'Story Line'),
              'ed_comp':fields.char('Comprehension of Language',size=100),
              'ed_entatin':fields.char('Entertainment/Level of Interest',size=100),
              'ed_relavance':fields.char('Relevance of Message',size=100),
              }
ed_rating_film()

class ed_channel(osv.osv):
    _name='ed.channel'
    _columns={
              'name':fields.char('Channel',size=200)
              }
ed_channel()


class ed_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
                'sch_terms' : fields.text('School Cinema Terms &amp; Conditions')
                }
ed_company()   

class ed_hub(osv.osv):
    _name = 'ed.hub'
    _columns = {
                'name' : fields.char('HUB',size=300)
                }
ed_hub() 

class ed_module(osv.osv):
    _name='ed.module'
    _columns={'name':fields.integer('Module')
              }
ed_module()   

class ed_school_strength(osv.osv):
    _name='ed.school.strength'
    
    _columns={'partner_id':fields.many2one('res.partner','Partner'),
              'ed_class':fields.selection(CLASS_STD,'Class', required = True),
              'ed_sec':fields.integer('Sections'),
              'ed_students':fields.integer('Total'),
              'ed_boys':fields.integer('Boys'),
              'ed_girls':fields.integer('Girls'),             
              }
ed_school_strength() 

class ed_day(osv.osv):
    _name='ed.day'
    _columns={
              'ed_seq':fields.integer('Sequence'),
              'name':fields.char('Description',size=200),
              }
ed_day() 

class ed_content(osv.osv):
    _name='ed.content'
    _columns={
              'name':fields.char('Description',size=200),
              'seq':fields.integer('Sequence'),
              }
ed_content()

class ed_topic(osv.osv):
    _name='ed.topic'
    _columns={
              'content_id':fields.many2one('ed.content','Content'),
              'ed_class':fields.selection(CLASS_STD,'Class'),
              'name':fields.char('Description',size=200),
              'seq':fields.integer('Sequence'),
              }
ed_topic()

class ed_time(osv.osv):
    _name='ed.time'
    _columns={
              #'name':fields.time('Time')
              'name':fields.datetime('Time')
              }
ed_time()

class ed_status(osv.osv):
    _name='ed.status'
    _columns={
              'name':fields.char('Status',size=100)
              }
ed_status()  

class ed_method_used(osv.osv):
    _name='ed.method.used'
    _columns={
              'name':fields.char('Methodology Used',size=100)
              }
ed_method_used()  

class ed_lesson(osv.osv):
    _name='ed.lesson'
    _columns={
              'name':fields.char('Lessons',size=100),              
              }
ed_lesson()  

class ed_film(osv.osv):
    _name='ed.film'
    _columns={
              'name':fields.char('Films',size=100),
              'ed_class':fields.selection(CLASS_STD,'STD'),              
              }
ed_film()  

class ed_grade(osv.osv):
    _name = 'ed.grade'
    _columns={
              'name':fields.char('Grade',size=5),
              'percent_from':fields.float('% From'),
              'percent_to':fields.float('% To'),
              }
    _order = 'name'
ed_grade()
 

class ed_sponsors(osv.osv):
    _name = 'ed.sponsors'
    _columns={
              'ed_skills' : fields.selection([('activity','Activity'),('akshaya','Akshaya')],'Skills'),
              'scity_id' : fields.many2one('ed.city','City'),
              'sponsor1' : fields.binary('Sponsor1'),
              'sponsor2' : fields.binary('Sponsor2'),
              'sponsor3' : fields.binary('Sponsor3'),
              'comp_id' : fields.many2one('res.company','Company'),              
              }   
ed_sponsors()


class ed_performance_review(osv.osv):
    _name = 'ed.performance.review'
    _columns={
              'name' : fields.char('Performance Review',size=100),
              'value' : fields.float('Value')
              }
    _order = 'value desc'
   
ed_performance_review()

class ed_skill_behave(osv.osv):
    _name = 'ed.skill.behave'
    _columns={
              'name' : fields.char('Skills',size=100),
              'desc' : fields.text('Description')
              }   
ed_skill_behave()

class ed_hr_training(osv.osv):
    _name = 'ed.hr.training'
    _description = "Training Need Analysis"
    _columns  = {
                'name' : fields.char('Description',size=100),
                 } 
ed_hr_training()  

class ed_initiator(osv.osv):
    _name = 'ed.initiator'
    _columns = {
              'name' : fields.char('Question',size=500),
              }   
ed_initiator()

class ed_hr_assess(osv.osv):
    _name = 'ed.hr.assess'
    _columns={
              'name' : fields.char('HR Parameters',size=250),
              'out_of' : fields.integer('Out Of')
              }   
ed_hr_assess()

class ed_hr_status(osv.osv):
    _name = 'ed.hr.status'
    _columns = {
              'name' : fields.char('Status',size=50),
              }   
ed_hr_status()  

class ed_company_work_time(osv.osv):
    _name = 'ed.company.work.time'
    _description = 'Company Work Timings'
    
    def _gen_sequence(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        
        for case in self.browse(cr,uid,ids):
            seq = 0
            if case.hr_day == 'mon':seq = 1
            elif case.hr_day == 'tue':seq = 2
            elif case.hr_day == 'wed':seq = 3
            elif case.hr_day == 'thu':seq = 4
            elif case.hr_day == 'fri':seq = 5
            elif case.hr_day == 'sat':seq = 6
            elif case.hr_day == 'sun':seq = 7   
            res[case.id] = seq
        return res
    
    _columns = {
                'depat_id' : fields.many2one('hr.department','Department',ondelete = 'cascade'),
                'hr_day' : fields.selection([('mon','Monday'),('tue','Tuesday'),('wed','Wednesday'),('thu','Thrusday'),('fri','Friday'),('sat','Saturday'),('sun','Sunday')],'Days'),
#                 'hr_start_date' : fields.time('Start Time'),
#                 'hr_end_date' : fields.time('End Time'),
                'hr_start_date' : fields.datetime('Start Time'),
                'hr_end_date' : fields.datetime('End Time'),
                'seq': fields.function(_gen_sequence, string='Sequence', method=True, store=True, type='integer'),
                }
    _order = 'seq'
    
    def unlink(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        empwork_obj = self.pool.get('ed.hr.emp.details')
        for case in self.browse(cr,uid,ids):
            emp_ids = emp_obj.search(cr,uid,[('department_id','=',case.depat_id.id)])
            for emp in emp_ids:
                empwork_ids = empwork_obj.search(cr,uid,[('hr_emp_id','=',emp),('hr_day','=',case.hr_day)])
                empwork_obj.unlink(cr,uid,empwork_ids)
        return super(ed_company_work_time, self).unlink(cr, uid, ids, context=context)
    
ed_company_work_time() 
               
class ed_synchronization_log(osv.osv):
    _name = 'ed.synchronization.log'
    _columns = {
                'dt_time' : fields.date('Date'),                            
                }
ed_synchronization_log()

class ed_peersuper_parameters(osv.osv):        
    _name = 'ed.peersuper.parameters'
    _columns ={'name':fields.char('Parameters',size=128),
               'type':fields.selection([('peer','Peer'),('supervisor','Supervisor')],'Type'),
            }
ed_peersuper_parameters()

class ir_model_access(osv.osv):
    _inherit = 'ir.model.access'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
               }
    
#    def check(self, cr, uid, model, mode='read', raise_exception=True, context=None):
#        
#        if uid==1:
#            # User root have all accesses
#            # TODO: exclude xml-rpc requests
#            return True
#
#        assert mode in ['read','write','create','unlink'], 'Invalid access mode'
#
#        if isinstance(model, browse_record):
#            assert model._table_name == 'ir.model', 'Invalid model object'
#            model_name = model.name
#        else:
#            model_name = model
#
#        # osv_memory objects can be read by everyone, as they only return
#        # results that belong to the current user (except for superuser)
#        model_obj = self.pool.get(model_name)
#        if isinstance(model_obj, osv.osv_memory):
#            return True
#
#        # We check if a specific rule exists
#        cr.execute('SELECT MAX(CASE WHEN perm_' + mode + ' THEN 1 ELSE 0 END) '
#                   '  FROM ir_model_access a '
#                   '  JOIN ir_model m ON (m.id = a.model_id) '
#                   '  JOIN res_groups_users_rel gu ON (gu.gid = a.group_id) '
#                   ' WHERE m.model = %s '
#                   '   AND gu.uid = %s '
#                   , (model_name, uid,)
#                   )
#        r = cr.fetchone()[0]
#
#        if r is None:
#            # there is no specific rule. We check the generic rule
#            cr.execute('SELECT MAX(CASE WHEN perm_' + mode + ' THEN 1 ELSE 0 END) '
#                       '  FROM ir_model_access a '
#                       '  JOIN ir_model m ON (m.id = a.model_id) '
#                       ' WHERE a.group_id IS NULL '
#                       '   AND m.model = %s '
#                       , (model_name,)
#                       )
#            r = cr.fetchone()[0]
#
#        if not r and raise_exception:
#            cr.execute('''select
#                    g.name
#                from
#                    ir_model_access a 
#                    left join ir_model m on (a.model_id=m.id) 
#                    left join res_groups g on (a.group_id=g.id)
#                where
#                    m.model=%s and
#                    a.group_id is not null and perm_''' + mode, (model_name, ))
#            groups = ', '.join(map(lambda x: x[0], cr.fetchall())) or '/'
#            msgs = {
#                'read':   _("You Do Not Have the Required Permissions to Complete this Transaction!"),
#                'write':  _("You Do Not Have the Required Permissions to Complete this Transaction!"),
#                'create': _("You Do Not Have the Required Permissions to Complete this Transaction! "),
#                'unlink': _("You Do Not Have the Required Permissions to Complete this Transaction!"),
#            }
#
#            raise except_orm(_('AccessError'), msgs[mode] % () )
#        return r
#    
#    check = tools.cache()(check)
#
#    __cache_clearing_methods = []
    
ir_model_access() 

class qualification_param(osv.osv):
    _name="qualification.param"
    
    _columns={
              'type':fields.selection([('curriculum','Curriculum'),('schl_strength','School Strength'),('socio_eco','Socio Economic Background'),('time_span','Time Span')],'Type'),
              'name':fields.char('Qualification Parameters',size=128),
              'points':fields.integer('Points')
             }    
qualification_param()

#class ir_attachment(osv.osv):
#    
#    _inherit = 'ir.attachment'
#    
#    def write(self, cr, uid, ids, vals, context=None):
#        self.check(cr, uid, ids, 'write', context=context, values=vals)
#        for case in self.browse(cr,uid,ids):
#            if case.create_uid.id != uid :
#               raise osv.except_osv(_('warning'),('You Do Not Have the Required Permissions to Complete this Transaction!'))
#        return super(ir_attachment, self).write(cr, uid, ids, vals, context)
#    
#    def unlink(self, cr, uid, ids, context=None):
#        self.check(cr, uid, ids, 'unlink', context=context)
#        for case in self.browse(cr,uid,ids):
#            if case.create_uid.id != uid :
#               raise osv.except_osv(_('warning'),('You Do Not Have the Required Permissions to Complete this Transaction!'))
#        return super(ir_attachment, self).unlink(cr, uid, ids, context)
#
#ir_attachment()


class act_window(osv.osv):
    _inherit = 'ir.actions.act_window'
    _columns = {'domain': fields.char('Domain Value', size=500,
            help="Optional domain filtering of the destination data, as a Python expression"),
               }    
act_window()     


class ed_contributors_section(osv.osv):
    _name='ed.contributors.section'
    _columns={
              'name' : fields.char('Section',size=128),
              } 
ed_contributors_section()   


class ed_contributors_details(osv.osv):
    _name='ed.contributors.details'
    _columns={
              'name'        : fields.char('Name',size=128),
              'institution' : fields.char('Institution',size=128),
              'contact'     : fields.char('Contact No.',size=128),
              'email'       : fields.char('Email',size=128),
              'designation' : fields.char('Designation',size=50),
              'address' : fields.char('Address',size=200),
              'area_of_wrk' : fields.char('Area Of Work',size=50),
              
              } 
    
    def name_get(self, cr, uid, ids, context=None):
        
        if not ids:
            return []
        res = []  
        for r in self.read(cr, uid, ids, ['name', 'institution', 'contact', 'email']):      
            cont_det = (r['name'] or '') + ' ,' + (r['institution'] or '') + ' ,' + (str(r['contact']) or '') + ' ,' + (r['email'] or '')
            res.append((r['id'], cont_det or '/'))
        return res

    
ed_contributors_details()    

class ed_advertisers_details(osv.osv):
    _name='ed.advertisers.details'
    _columns={
              
              'institution' : fields.char('Institution',size=128),
              'contact'     : fields.char('Contact No.',size=15),
              'email'       : fields.char('Email',size=50),
              'address'     : fields.char('Address',size=200),
              'type'        : fields.selection([('paid','Paid'),('discounted','Discounted'),('partner','Partner')],'Type'),
              } 
    
    def name_get(self, cr, uid, ids, context=None):
        
        if not ids:
            return []
        res = []  
        for r in self.read(cr, uid, ids, [ 'institution', 'contact','email']):      
            cont_det = (r['institution'] or '') + ' ,' + (r['contact'] or '') + ' ,' + (r['email'] or '')
            res.append((r['id'], cont_det or '/'))
        return res

    
ed_advertisers_details() 

class ed_director_details(osv.osv):
    _name='ed.director.details'
    _columns={
              
              'name' : fields.char('Name',size=128),
              'contact'     : fields.char('Contact No.',size=15),
              'email'       : fields.char('Email',size=50),
              'address'     : fields.char('Address',size=100),
              'country_id'  : fields.many2one('res.country','Country'),
              'state_id'    : fields.many2one('res.country.state','State'),
              'city_id'     : fields.many2one('ed.city','City'),
              'zip'         : fields.char('Zip',size=6),
              } 
    
    def name_get(self, cr, uid, ids, context=None):
        
        if not ids:
            return []
        res = []  
        for r in self.read(cr, uid, ids, [ 'name','address','address1','state_id','city_id','contact','email']):      
            cont_det = (r['name'] or '') + ' ,' + (r['address'] or '') + ' ,' + (r['address1'] or '') + ' ,' + (r['state_id'] and r['state_id'][1] or '')  + ' ,' + (r['city_id'] and r['city_id'][1] or '') + ' ,' + (r['contact'] or '') + ' ,' + (str(r['email']) or '')
            res.append((r['id'], cont_det or '/'))
        return res

    
ed_director_details() 

class ed_year(osv.osv):
    _name='ed.year'
    _columns={              
              'name' : fields.char('Year',size=4),              
              }      
ed_year() 

class ed_advertisers_position(osv.osv):
    _name='ed.advertisers.position'
    _columns={              
              'name' : fields.char('Position',size=50),              
              }      
ed_advertisers_position() 
                                                                                        