from openerp.osv import fields,osv
from openerp.tools.translate import _
import config
import time
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import datetime
import re
from dateutil import parser
import openerp.tools
    
class ed_subscription(osv.osv): 
    _name='ed.subscription'
    
    
    def _get_issues(self,cr,uid,ids,name,args,context=None): 
        res={}
    
        for this in self.browse(cr,uid,ids,context):
            res[this.id]={'no_issues':False,'end_date':False}
            issues=self.onchange_Terms(cr,uid,ids,this.start_date,this.term)
            if issues:
                res[this.id]['end_date']=issues['value']['end_date']
                res[this.id]['no_issues']=issues['value']['no_issues']
                
        return res
    
    def _get_address(self,cr,uid,ids,name,args,context=None): 
        res={}
        addr = ''
        address_obj = self.pool.get('res.partner')
        for this in self.browse(cr,uid,ids,context):                        
            if this.partner_id and this.receive_addr == 'instute_addr':
                address_id = address_obj.search(cr,uid,[('partner_id','=',this.partner_id.id)])[0]
                address = address_obj.browse(cr,uid,address_id)
                addr += address.street or ''
                addr += address.street2 or ''
                addr += address.country_id and address.country_id.name or ''
                addr += address.state_id and address.state_id.name or ''
                addr += address.ed_city_id and address.ed_city_id.name or ''
            else:
                addr = this.resi_add or ''
            res[this.id] = addr
        return res   

    _columns={
              'sub_no'       : fields.char('Reference',size=10),
              'partner_id'   : fields.many2one('res.partner','School',size=128,states={'confirmed': [('readonly', True)]}),
              'start_date'   : fields.date('Start Date',required=True,states={'confirmed': [('readonly', True)]}),
              'end_date'     : fields.function(_get_issues,method=True,store=True,type='date',multi='issues',string='End Date'),
              'term'         : fields.selection(config.CLASS_STD,'TERM',states={'confirmed': [('readonly', True)]}),
              'no_issues'    : fields.function(_get_issues,method=True,store=True,type='integer',multi='issues',string='No of Issues'),
              'address'      : fields.function(_get_address,method=True,store=True,type='char',string='Address',size=300),
              'amount'       : fields.float('Amount',states={'confirmed': [('readonly', True)]}),
              'bank'         : fields.char('Bank',size=128,states={'confirmed': [('readonly', True)]}),
              'paymnt_date'  : fields.date('Payment Date',states={'confirmed': [('readonly', True)]}),
              'chck_num'     : fields.char('Check Number',size=128,states={'confirmed': [('readonly', True)]}),
              'name'         : fields.char('Name',size=128,states={'confirmed': [('readonly', True)]}),
              'dob'          : fields.date('Date Of Birth',states={'confirmed': [('readonly', True)]}),
              'tenure'       : fields.char('Tenure as a Principal in the Present School',size=128,states={'confirmed': [('readonly', True)]}),
              'resi_add'     : fields.char('Residential Address', size=128,states={'confirmed': [('readonly', True)]}),
              'contact_no'   : fields.char('Contact No.',size=10,states={'confirmed': [('readonly', True)]}),
              'email'        : fields.char('Email',size=128,states={'confirmed': [('readonly', True)]}),
              'edu_bkgrnd'   : fields.char('Educational Background',size=128,states={'confirmed': [('readonly', True)]}),
              'no_copies'    : fields.integer('No. Of. Copies',states={'confirmed': [('readonly', True)]}),
              'receive_addr' : fields.selection([('instute_addr','Institutional Address'),
                                                 ('resident_addr','Residential Address')],'I would like to receive MENTOR on',states={'confirmed': [('readonly', True)]}),
              'state'        : fields.selection([
                                                ('pending', 'Pending'),
                                                ('confirmed', 'Confirmed'),
                                                ('cancel','Canceled'),
                                                ('closed','Closed')], 'State', readonly=True, select=True),
              'payment_type' : fields.selection([
                                                 ('cash','Cash')
                                                 ,('cheque','Cheque')
                                                 ,('bank','Bank')
                                                 ,('statement','Statement')
                                                 ,('c_d_card','Credit/Debit Card')],'Payment Type',states={'confirmed': [('readonly', True)]}),              
              }
    _defaults={
               'state': 'pending',
               'no_copies' : 1,
               'receive_addr' : 'resident_addr'
               }

    def onchange_Terms(self,cr,uid,ids,start_date,term):
        result={}
        if not term:
            term = 0
        if start_date!=False:
           no_issues = term*12
#           end_date= datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(years=(term))
           end_date = (parser.parse(start_date)+ relativedelta(years =(term))).strftime('%Y-%m-%d')
           end_date = (parser.parse(end_date)- relativedelta(days =1)).strftime('%Y-%m-%d')
           result['no_issues']= no_issues
           result['end_date']= end_date
        else:
           result={'no_issues':False,'end_date':False}    
        return {'value':result}
    
    def onchange_Partner(self,cr,uid,ids,partner_id):
        result={}
        if partner_id:
              result['receive_addr']= 'instute_addr'
        else:
           result={'receive_addr':'resident_addr'}    
        return {'value':result}
    
    def onchange_ReceiveType(self,cr,uid,ids,receive_addr,partner_id):
        result={}        
        warning = {}
        if not partner_id and receive_addr and receive_addr == 'instute_addr':
              result['receive_addr'] ='resident_addr'              
              warning = {
                    'title': _('Warning!'),
                    'message': _('You are unable to select type as Institutional Address unless you select the School.')}
                
        else:
           result['receive_addr'] = receive_addr    
        return {'value':result, 'warning': warning}    
    
    def action_send(self, cr, uid, ids, context=None):
        """ This sends an Thank You email to Subscribers on Confirmation
        """        
        mail_obj = self.pool.get('crm.send.mail')
        Addr_obj = self.pool.get('res.partner')
        user = self.pool.get('res.users').browse(cr, uid,uid)
        for case in self.browse(cr,uid,ids):
            if case.receive_addr == 'resident_addr':               
               email_to = case.email
            else:                
               email_to = case.partner_id.email
                 
            subtype = 'plain'
            comp_email = ''
            addr_id = Addr_obj.search(cr,uid,[('partner_id','=',user.company_id.id)])[0]
            comp_email = Addr_obj.browse(cr,uid,addr_id).email 
                
            email_from = user.user_email
            email_cc = comp_email or ''
            
            if not email_from:
                raise osv.except_osv(_('Error'), _("Please enter " + str(case.user_id.name) + "'s Email id!"))
                
            if not email_to:
                raise osv.except_osv(_('Error'), _("Please enter " + str(case.partner_id and case.partner_id.name or case.name) + "'s Email id!"))
                
            emails = re.findall(r'([^ ,<@]+@[^> ,]+)', email_to or '')
            email_cc = re.findall(r'([^ ,<@]+@[^> ,]+)', email_cc or '')
            emails = filter(None, emails)            
            subject = 'Greetings from MENTOR!'
            body = """ To,   

""" + str(case.partner_id and case.partner_id.name or '') + """

 

Dear Sir/Madam """ + str(case.name or '') + """,

 

Greetings from MENTOR!

 

Let me at the outset thank you for subscribing to Mentor. This gesture of yours will go a long way in making Mentor a positive force in the educational arena, thus making it stronger to wield and weather the challenges of the future.

 

Your subscription is valid from the month of """ + str(case.start_date) + """ and will be renewed by """ + str(case.end_date) + """, while your subscription number for all further correspondence in this regard will be TA-2041/01-13.  All other communication with reference to the magazine will be posted to you from our office timely.

 

We value your partnership and relationship with us and trust you will contribute to the magazine in a big way. Please do not hesitate to write to us with queries, suggestions and comments whenever required. Our endeavor would be to ensure that every measure is taken to roll out the best to educators across the globe.

 

Thank you and we look forward to a very fruitful relationship with you in the future!

 

Regards,

 

Syed Sultan Ahmed

Managing Director"""
                
                
            if emails and email_from: 
                flag = tools.email_send(
                    email_from,
                    emails,
                    subject, 
                    body,
                    email_cc = email_cc,
                    attach = [],
                    subtype = subtype,
                    reply_to = email_from,
                    openobject_id = str(case.id),
                    x_headers = {}
                )

                if not flag:
                    raise osv.except_osv(_('Error!'), _('Unable to send mail. Please check SMTP is configured properly.'))
 
        return True

#    def Subscription_Reminder(self, cr, uid, ids, context=None):
    def Subscription_Reminder(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        """ This sends an Thank You email to Subscribers on Confirmation
        """        
        mail_obj = self.pool.get('crm.send.mail')
        Addr_obj = self.pool.get('res.partner') 
        Addr_obj = self.pool.get('res.partner')
        cr.execute("SELECT id \
                    FROM ed_subscription s \
                    WHERE s.state = 'confirmed' AND (s.end_date IN (SELECT now():: DATE + 45 ) \
                    OR s.end_date IN (SELECT now():: DATE + 30) \
                    OR s.end_date IN (SELECT now():: DATE + 15));")
        subscrip_ids = cr.fetchall()
        
        user = self.pool.get('res.users').browse(cr, uid,uid)
        for sub in subscrip_ids:
                case = self.browse(cr,uid,sub[0])
                if case.receive_addr == 'resident_addr':               
                   email_to = case.email
                else:                
                   email_to = case.partner_id.email
                     
                subtype = 'plain'
                comp_email = ''
                addr_id = Addr_obj.search(cr,uid,[('partner_id','=',user.company_id.id)])[0]
                comp_email = Addr_obj.browse(cr,uid,addr_id).email 
                    
                email_from = comp_email 
                email_cc = comp_email or ''
                
                if not email_from:
                    raise osv.except_osv(_('Error'), _("Please enter Company's Email id!"))
                    
#                if not email_to:
#                    raise osv.except_osv(_('Error'), _("Please enter " + str(case.partner_id and case.partner_id.name or case.name) + "'s Email id!"))
                    
                emails = re.findall(r'([^ ,<@]+@[^> ,]+)', email_to or '')
                email_cc = re.findall(r'([^ ,<@]+@[^> ,]+)', email_cc or '')
                emails = filter(None, emails)            
                subject = 'Reminder from MENTOR!'
                body = """ To,   
    
    """ + str(case.partner_id and case.partner_id.name or '') + """    
    
    Dear Sir/Madam """ + str(case.name or '') + """,
    
    Your MENTOR Subscription may last at the date """ + str(case.end_date) + """ . Please renew it as soon as possible.    
    Thank you and we look forward to a very fruitful relationship with you in the future!    
    
    Regards,   
    Syed Sultan Ahmed   
    Managing Director"""
                    
                    
                if emails and email_from: 
                    flag = tools.email_send(
                        email_from,
                        emails,
                        subject, 
                        body,
                        email_cc = email_cc,
                        attach = [],
                        subtype = subtype,
                        reply_to = email_from,
                        openobject_id = str(case.id),
                        x_headers = {}
                    )
    
                    if not flag:
                        raise osv.except_osv(_('Error!'), _('Unable to send mail. Please check SMTP is configured properly.'))
 
        return True

    def action_confirm(self,cr,uid,ids,context=None):
        
        partner_obj = self.pool.get('res.partner')
        for case in self.browse(cr,uid,ids):
            self.write(cr, uid, ids, {'state': 'confirmed'})
            if case.partner_id:
               partner_obj.write(cr,uid,[case.partner_id.id],{'ed_sh_subscrip':True})
#        self.action_send(cr, uid, ids, context)
        return True
    
    def button_cancel(self,cr,uid,ids,context=None):
        
        partner_obj = self.pool.get('res.partner')
        for case in self.browse(cr,uid,ids):
            self.write(cr, uid,ids, {'state': 'cancel'})
            if case.partner_id:
               partner_obj.write(cr,uid,[case.partner_id.id],{})
        return True
 
    def button_set_to_draft(self,cr,uid,ids,context=None):
        self.write(cr, uid,ids, {'state': 'pending'})
        return True
    
      
    
ed_subscription() 

def _get_year(self, cr, uid, context=None):
    res = {}
    year = int(time.strftime('%Y'))    
    return [((year+r),(str(year+r))) for r in range(5)]

class ed_monthly_edition(osv.osv):
    _name='ed.monthly.edition'
     
    _columns={
              'month': fields.selection(config.MONTH, 'Month',states={'confirmed': [('readonly', True)]}),
              'year'  : fields.many2one('ed.year','Year',states={'confirmed': [('readonly', True)]}),
              'subscriber_ids' : fields.many2many('ed.subscription','monthly_subs_rel','monthly_id','subs_id','Subscriber'),
              'compliment_ids'  : fields.many2many('res.partner','part_comp_rel','comp_id','partner_id','Compliment',order='id'),
              'contribu_ids' : fields.one2many('ed.contributors','monthly_id','Contributors',states={'confirmed': [('readonly', True)]}),
              'adverti_ids' : fields.many2many('ed.advertisers.details','monthly_adver_rel','monthly_id','adver_id','Advertisers'),
              'director_ids' : fields.many2many('ed.director.details','monthly_direc_rel','monthly_id','director_id','Directors'),
              'vw_subscriber_ids' : fields.one2many('vw.ed.subscription','monthly_id','View Subscriber'),
              'vw_adverti_ids' : fields.one2many('vw.ed.advertisers','monthly_id','View Advertisers'),
              'vw_director_ids' : fields.one2many('vw.ed.director','monthly_id','View Director'),
              'state': fields.selection([
                 ('draft', 'Draft'),
                 ('confirmed', 'Confirmed'),('cancel','Canceled')], 'State', readonly=True,select=True),
              
              }
    _order='id desc'
    _defaults={
               'state': 'draft',
               }
   
   
    def create(self, cr, uid, vals, context=None):
        edition = [
                ('month', '=', vals.get('month')),
                ('year', '=', vals.get('year'))
        ]
        edition_id = self.search(cr, uid, edition)
        if edition_id:
            raise osv.except_osv(_('Error'), _('You cannot have two records of same month and year'))         
        return super(ed_monthly_edition,self).create(cr,uid,vals,context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        
        for case in self.browse(cr,uid,ids):
            if 'month' in vals and vals['month'] != case.month or 'year' in vals and vals['year'] != case.year.id:
        
                    edition = [
                            ('month', '=', vals.get('month')),
                            ('year', '=', vals.get('year'))
                    ]
                    edition_id = self.search(cr, uid, edition)
                    if edition_id:
                        raise osv.except_osv(_('Error'), _('You cannot have two records of same month and year'))  
        return super(ed_monthly_edition,self).write(cr,uid,ids,vals,context=context)

# Creating the DO record
    def create_delivery_order(self,cr,uid,ids,context=None):
        
        month = {1: 'January', 2: 'February', 3:'March', 4:'April', 5:'May', 6: 'June', 7 : 'July', 8:'August' ,9: 'September', 10:'October' , 11:'November' , 12:'December' }
        partner_obj = self.pool.get('res.partner')
        for case in self.browse(cr,uid,ids):
            self.write(cr, uid, ids, {'state': 'confirmed'})
            for p in case.compliment_ids:
                partner_obj.write(cr,uid,[p.id],{'ed_sh_complem':True})
            picking_id = False
            move_obj = self.pool.get('stock.move')
            proc_obj = self.pool.get('procurement.order')
            prod_obj = self.pool.get('product.product')
            tmplate_obj = self.pool.get('product.template')
                        
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id
            sc_qty = 0 
            for sc in case.subscriber_ids:
                sc_qty += sc.no_copies
                
            mon_qty = sc_qty + len(case.compliment_ids) + len(case.contribu_ids) + len(case.adverti_ids) + len(case.director_ids)
            
#            date_planned = datetime.strftime() + relativedelta(days=0)
#            date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')
            date_planned = time.strftime('%Y-%m-%d %H:%M:%S')
            
            location = self.pool.get('stock.location').search(cr,uid,[('name','=','Stock')],limit=1)
            destination = self.pool.get('stock.location').search(cr,uid,[('name','=','Customers')],limit=1)
            
            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                'name': pick_name,
                'origin': 'Monthly Edition',
                'type': 'out',
                'state': 'draft',
                'move_type': 'direct',
                'invoice_state': 'none',
                'company_id': company.id,
                'monthly_id': case.id,
                'service_type':'mentor'
            })
            
            p_name = 'Mentor Magazines - ' + month[case.month] + '/' + str(case.year)                     
            products = prod_obj.search(cr,uid,[('name_template', '=', p_name)],limit=1)
            
            if not products:
               tmplate_id = tmplate_obj.create(cr, uid, {
                                                          'warranty'      : 0.00
                                                         ,'list_price'    : 0.00
                                                         ,'weight'        : 0
                                                         ,'standard_price': 0.00 
                                                         ,'name'          : p_name
                                                         })
               if tmplate_id:
                   prod_id = prod_obj.create(cr,uid,{'name_template'   : p_name
                                                    ,'product_tmpl_id' : tmplate_id
                                                    ,'display_unit'    : '-'})
                   products.append(prod_id)
            for prod in prod_obj.browse(cr,uid,products):
                
                move_id = self.pool.get('stock.move').create(cr, uid, {
                    'name': prod.name_template,
                    'picking_id': picking_id,
                    'product_id': prod.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'product_qty': mon_qty,
                    'product_uom': prod.uom_id.id,
                    'product_uos_qty': mon_qty,
                    'product_uos': prod.uom_id.id,
                    'location_id': location[0],
                    'location_dest_id': destination[0],
                    'tracking_id': False,
                    'state': 'draft',
                    'company_id': company.id,
                })        
        
        return True
     
    def button_cancel(self,cr,uid,ids,context=None):
        picking_obj = self.pool.get('stock.picking')
        for case in self.browse(cr,uid,ids):
            pick_id=picking_obj.search(cr,uid,[('state','=','done'),('monthly_id','=',case.id)],order = 'id desc',limit=1)
            if len(pick_id):
                raise osv.except_osv(_('Error'), _('You cannot CANCEL the record which is in DONE state'))
            else:
                pick_id=picking_obj.search(cr,uid,[('monthly_id','=',case.id),('state','in',['draft','cancel'])],order = 'id desc',limit=1)
                picking_obj.unlink(cr,uid,pick_id,context)
                self.write(cr, uid,ids, {'state': 'cancel'})
        return True


    def button_set_to_draft(self,cr,uid,ids,context=None):
        self.write(cr, uid,ids, {'state': 'draft'})
        return True       
        
    def button_populate(self,cr,uid,ids,context=None):
        
        partner_obj = self.pool.get('res.partner')
        subscription_obj = self.pool.get('ed.subscription')
        director_obj = self.pool.get('ed.director.details')       
        DATETIME_FORMAT = "%Y-%m"
        
        monthly_ids = self.search(cr,uid,[('state','=','confirmed')],limit = 1) 
        Month_ed = False        
        cmply_ids = set()
        if monthly_ids:
           Month_ed = self.browse(cr,uid,monthly_ids[0])
           #prev record complimentry ids
           for cm in Month_ed.compliment_ids:
               cmply_ids.add(cm.id)
                   
        for case in self.browse(cr,uid,ids):
            conv_date = str(case.year.name)+ """-""" +str(case.month) 
            edi_date = datetime.datetime.strptime(conv_date, DATETIME_FORMAT)
            
            cr.execute("""SELECT id FROM ed_subscription WHERE '""" + str(edi_date) +"""'::DATE BETWEEN start_date::DATE AND end_date ::DATE
                          AND state = 'confirmed'""")
            subscrip = cr.fetchall()
            print "subscrip",subscrip
            
            cr.execute("""SELECT distinct(advert_det_id) FROM ed_advertisers WHERE '""" + str(edi_date) +"""'::DATE BETWEEN st_date::DATE AND ed_date ::DATE
                                                                                                         AND state = 'confirmed'
                      """)
            advertise = cr.fetchall()
            print "advertise",advertise
            
            #current record complimentry ids
            for c in case.compliment_ids:
                cmply_ids.add(c.id)
            director_ids = director_obj.search(cr,uid,[])          
            self.write(cr,uid,[case.id],{'subscriber_ids':[(6, 0, subscrip)],
                                         'compliment_ids':[(6, 0, list(cmply_ids))],
                                         'director_ids' : [(6, 0, director_ids)],
                                         'adverti_ids' :  [(6, 0, advertise)]
                                         }
                       )       
                
        return True   
 
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        tens = {1: 'January', 2: 'February', 3:'March', 4:'April', 5:'May', 6: 'June', 7 : 'July', 8:'August' ,9: 'September', 10:'October' , 11:'November' , 12:'December' }
        reads = self.read(cr, uid, ids, ['month','year'], context=context)
        res = []
        for record in reads:
            name = record['month']
            if record['year']:
                name = tens[name] + '-' + (record['year']and record['year'][1] or '') 
            res.append((record['id'], name))
        return res


ed_monthly_edition()

class ed_contributors(osv.osv):
    _name='ed.contributors'
    _columns={
              'section_id' : fields.many2one('ed.contributors.section','Section'),
              'monthly_id' : fields.many2one('ed.monthly.edition','Monthly Edition'),
              'contributors_id' : fields.many2one('ed.contributors.details','Contributors'),
              'article_title' : fields.char('Article Title',size=128),                           
              }    
    _order = 'monthly_id desc,section_id'
ed_contributors()
 
class ed_advertisers(osv.osv):
     _name='ed.advertisers'
     _columns={
               'st_date' : fields.date('Start Date' ,states={'confirmed': [('readonly', True)]}),
               'ed_date' : fields.date('End Date',states={'confirmed': [('readonly', True)]}),
               'advert_det_id' : fields.many2one('ed.advertisers.details','Advertisers Details',states={'confirmed': [('readonly', True)]}),
               'position_id' :fields.many2one('ed.advertisers.position','Position',states={'confirmed': [('readonly', True)]}),
               'price' : fields.float('Price',states={'confirmed': [('readonly', True)]}),
               'state'        : fields.selection([('pending', 'Pending'),
                                                ('confirmed', 'Confirmed'),
                                                ('cancel','Canceled'),
                                                ('closed','Closed')], 'State', readonly=True, select=True),
               }
     _order = 'st_date desc, ed_date desc'
     _defaults ={'state':'pending'}
          
     def action_confirm(self,cr,uid,ids,context=None):
        
        details_obj = self.pool.get('ed.advertisers.details')
        for case in self.browse(cr,uid,ids):
            self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
     def button_cancel(self,cr,uid,ids,context=None):
        
        details_obj = self.pool.get('ed.advertisers.details')
        for case in self.browse(cr,uid,ids):
            self.write(cr, uid,ids, {'state': 'cancel'})
        return True
 
     def button_set_to_draft(self,cr,uid,ids,context=None):
        self.write(cr, uid,ids, {'state': 'pending'})
        return True
    
ed_advertisers()


