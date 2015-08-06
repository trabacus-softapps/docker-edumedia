from openerp.osv import fields,osv 
from openerp.tools.translate import _
import time


class crm_lead(osv.osv): 
    _inherit='crm.lead'    
    
#    def _get_partner_board(self, cr, uid, ids, name, args, context=None):
#        res = {}         
#        for case in self.browse(cr, uid, ids):
#            res[case.id] = False
#            if case.partner_id: 
#                res[case.id] = case.partner_id and case.partner_id.ed_board_id.id
#        return res
    
    def _get_default_stage(self, cr, uid, context=None):  
        stage = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Raw'),('type','=','opportunity')])
        
        return stage and stage[0] or False
    
#    def _get_channel(self, cr, uid, ids, name, args, context=None):
#        res = {}        
#        for case in self.browse(cr, uid, ids):
#            cr.execute("SELECT array_to_string(array(select name from ed_channel where id in (select channel_id from ed_lead_channel_rel where leads_id = %d)), ', ')" %(case.id))
#            res[case.id] = cr.fetchone()[0]
#        return res
    
    def _get_address(self, cr, uid, ids, name, args, context=None):
        res = {}        
        for case in self.browse(cr, uid, ids):
            res[case.id] = ''
            if case.partner_address_id:            
                res[case.id] = (case.partner_address_id.street or '') + " " + (case.partner_address_id.street2 or '')                
        return res
    
    def _get_strength(self, cr, uid, ids, name, args, context=None):
        res = {}        
        for case in self.browse(cr, uid, ids):
            res[case.id] = case.partner_id and case.partner_id.ed_total_strg or 0
        return res
    
    def _get_priority(self, cr, uid, ids, name, args, context=None):
        res = {}
        total = 0
        param_obj = self.pool.get('qualification.param')        
        for case in self.browse(cr, uid, ids):
            total  = case.curriculum_id and case.curriculum_id.points or 0 
            total += case.strength_id and case.strength_id.points or 0 
            total += case.time_id and case.time_id.points or 0 
            total += case.economic_id and case.economic_id.points or 0  
            if total >= 9 and total <= 11:
                res[case.id] = 'High Potential'
            elif total >= 6 and total <= 8:
                res[case.id] = 'Medium Potential'
            elif total >= 4 and total <= 5:
                res[case.id] = 'Low Potential'
            elif total <= 3 :
                res[case.id] = 'Lowest Potential'
                                
        return res
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        
        search_name = 'ed_crm_case_leads_filter'
        
        if 'vw_type' in context:
            vw_type = context.get('vw_type',False)
            if vw_type == 'sales_t':
               search_name = 'ed.crm.lead.report.select'
            elif vw_type == 'leads':
                search_name = 'ed_crm_case_leads_filter'
            else :
                search_name = 'ed_view_crm_case_create_leads_search'
                      
        if view_type == 'search':
           view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', search_name)])   
                         
        if view_id and isinstance(view_id, (list, tuple)):
           view_id = view_id[0] 
        return super(crm_lead,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

     
    _columns = {'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null',required=True,states={'done': [('readonly', True)]}, 
                              select=True, help="Optional linked partner, usually after conversion of the lead"),
                'partner_address_id': fields.many2one('res.partner', 'Partner Contact', \
                                 domain="[('partner_id','=',partner_id)]", states={'done': [('readonly', True)]}),    
                'email_from': fields.char('Email', size=128, help="E-mail address of the contact",states={'done': [('readonly', True)]}),
                'con_person':fields.char('Contact Person',size=128,states={'done': [('readonly', True)]}),
                'con_email':fields.char('Contact Email',size=128,states={'done': [('readonly', True)]}),
                'con_phone':fields.char('Contact Phone',size=128,states={'done': [('readonly', True)]}),
                'rmks' : fields.char('Remarks',size=300,states={'done': [('readonly', True)]}),
                'modules' : fields.char('Proposal Given for Modules',size=128,states={'done': [('readonly', True)]}),
                'propsal_no' : fields.char('Proposal Number',size=128),
                'prop_stu' : fields.integer('Proposal Given for (No. Of Students)',states={'done': [('readonly', True)]}),
                'rate_child' : fields.float('Rate Quoted Per Child',digits=(3,2),states={'done': [('readonly', True)]}),
                'exp_bill' : fields.float('Expected Billing',digits=(3,2),states={'done': [('readonly', True)]}),
                'background' : fields.text('School Background',states={'done': [('readonly', True)]}),
                'rsn_reject' : fields.text('Relationship Manager Remarks',states={'done': [('readonly', True)]}),
                'rgn_rmks' : fields.text('Regional Head Remarks',states={'done': [('readonly', True)]}),
                'user_id': fields.many2one('res.users', 'Eduvisor',help='By Default Salesman is Administrator when create New User',states={'done': [('readonly', True)]}),
                'state': fields.selection([('draft', 'Raw'),('qualified','Qualified Assigned'),('activate','Activated'),('open', 'Meeting/Proposal'),('cancel', 'Rejected'),('done','Moved TO CRM')], 'Stage', size=16, readonly=True,
                                  help='The state is set to \'Draft\', when a case is created.\
                                  \nIf the case is in progress the state is set to \'Open\'.\
                                  \nWhen the case is over, the state is set to \'Done\'.\
                                  \nIf the case needs to be reviewed then the state is set to \'Pending\'.'),
                'priority': fields.function(_get_priority, method=True, string='Priority',type='char',size = 64, store=True),
                'chanel_id': fields.many2one('ed.channel','Channel',states={'done': [('readonly', True)]}),
                'fed_state': fields.related('partner_address_id', 'state_id', type="many2one", relation='res.country.state', string='State', store=True),
                'city': fields.related('partner_address_id', 'ed_city_id', type="many2one", relation='ed.city', string='City', store=True),
                'pincode': fields.related('partner_address_id', 'zip', type="char", size=24, string='Pincode'),
                'contact': fields.related('partner_address_id', 'name', type="char", size=64, string='Contact'),
                'desig': fields.related('partner_address_id', 'ed_desig_id', type="many2one", relation='ed.designation', string='Designation'),
                'mobile': fields.related('partner_address_id', 'mobile', type="char", size=64, string='Mobile'),
                'phone': fields.related('partner_address_id', 'phone', type="char", size=64, string='Phone'),
                'c_email': fields.related('partner_address_id', 'email', type="char", size=240, string='email'),
                'sch_strength': fields.function(_get_strength, method=True, type="integer", string='School Strength'),
                'address': fields.function(_get_address, method=True, string='Address', type='char', size=300),    
                'nbr': fields.integer('# Leads',readonly=True),
                'curriculum_id':fields.many2one('qualification.param','Curriculum',states={'done': [('readonly', True)]}),
                'strength_id':fields.many2one('qualification.param','School Strength',states={'done': [('readonly', True)]}),
                'time_id':fields.many2one('qualification.param','Time Span',states={'done': [('readonly', True)]}),
                'economic_id':fields.many2one('qualification.param','Socio Economic Background',states={'done': [('readonly', True)]}),   
                'grades':fields.selection([('kg1','KG 1-2 (LKG/UKG)'),('one','1st-4th Std'),('five','5th-7th Std'),('eight','8th-10th Std'),('eleven','11th-12th Std')],'Grades Offered',states={'done': [('readonly', True)]}),
                'grades_desc'  :fields.char('Enter Specific Grades',size=50),             
                'annual_fees':fields.float('Annual School Fees',states={'done': [('readonly', True)]}),
                'sole_dsc':fields.selection([('yes','Yes'),('no','No')],'Sole Decision',states={'done': [('readonly', True)]}),         
                'sl_dsc_maker':fields.char('Decision Maker Name',size=128,states={'done': [('readonly', True)]}),
                'sl_dsign':fields.char('Designation',size=128,states={'done': [('readonly', True)]}),
                'sl_contact':fields.char('Contact Details',size=128,states={'done': [('readonly', True)]}),
                'msc' : fields.boolean('Moral Science Class',states={'done': [('readonly', True)]}),
                'vec' : fields.boolean('Value Education Class',states={'done': [('readonly', True)]}),
                'lssc' : fields.boolean('Life-Skills Sessions Class',states={'done': [('readonly', True)]}),
                'con' : fields.boolean('Counsellor',states={'done': [('readonly', True)]}),
                'none' : fields.boolean('None',states={'done': [('readonly', True)]}),
                'others' : fields.boolean('Others',states={'done': [('readonly', True)]}),
                'effec_med':fields.selection([('yes','Yes'),('maybe','Maybe'),('no','No')],'Effective Medium',states={'done': [('readonly', True)]}),
                'implement':fields.selection([('yes','Yes'),('maybe','Maybe'),('no','No')],'Implement',states={'done': [('readonly', True)]}),
                'remks1':fields.char('Remarks 1',size=256,states={'done': [('readonly', True)]}),
                'remks2':fields.char('Remarks 2',size=256,states={'done': [('readonly', True)]}),
                'time_span':fields.selection([('seven','Within 7 days'),('fifteen','7-15 days'),('thirty','15-30 days'),('other','Other')],'When do you want to hear from us?',states={'done': [('readonly', True)]}),
                'time_date':fields.date('Date',states={'done': [('readonly', True)]}),
                'oth_days':fields.char('Enter Days',size=15,states={'done': [('readonly', True)]}),
                'text1':fields.text('Text1',states={'done': [('readonly', True)]}),
                'text2':fields.text('Text2',states={'done': [('readonly', True)]}),
                'text3':fields.text('Text3',states={'done': [('readonly', True)]}),    
               }
    _defaults={
               'stage_id':_get_default_stage,
               'nbr':1,
               'priority':'Lowest Potential',
               'type':'opportunity'
               }
    
    def button_assign(self, cr, uid, ids, context={}):
        stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Qualified Assigned'),('type','=','opportunity')])[0] 
        self.write(cr, uid, ids, {'state': 'qualified','stage_id':stage_id})
        return True
    
    def button_activate(self, cr, uid, ids, context={}):
        stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Activated'),('type','=','opportunity')])[0]
        self.write(cr, uid, ids, {'state': 'activate','stage_id':stage_id})
        return True
    
    def button_prospect(self, cr, uid, ids, context={}):
        stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Meeting/Proposal'),('type','=','opportunity')])[0]
        self.write(cr, uid, ids, {'state': 'open','stage_id':stage_id})
        return True
    
    def onchange_partner_id(self, cr, uid, ids, part, email=False):
        
        partner_obj = self.pool.get('res.partner')    
        data = super(crm_lead,self).onchange_partner_id(cr, uid, ids, part, email=False)['value']
        partner = partner_obj.browse(cr,uid,part).ed_sh_cinema
        if partner:
           cr.execute("select id from crm_lead where partner_id=%d order by id desc limit 1"%(part)) 
           crm_ids = cr.fetchone()
           if crm_ids:   
              for case in self.browse(cr,uid,[crm_ids[0]]):
                  data.update({'con_person'   : case.con_person,
                               'con_email'    : case.con_email,
                               'con_phone'    : case.con_phone,                                  
                               'chanel_id'    : case.chanel_id and case.chanel_id.id or False,
                               'rmks'         : case.rmks,
                               'propsal_no'   : case.propsal_no,
                               'modules'      : case.modules,
                               'prop_stu'     : case.prop_stu,
                               'rate_child'   : case.rate_child,
                               'exp_bill'     : case.exp_bill,
                               'title_action' : case.title_action,
                               'date_action'  : case.date_action,
                               'background'   : case.background,
                               'rsn_reject'   : case.rsn_reject,
                               'rgn_rmks'     : case.rgn_rmks,
                               'curriculum_id': case.curriculum_id and case.curriculum_id.id or False,
                               'strength_id'  : case.strength_id and case.strength_id.id or False,
                               'time_id'      : case.time_id and case.time_id.id or False,
                               'economic_id'  : case.economic_id and case.economic_id.id or False,
                               'grades'       : case.grades,
                               'grades_desc'  : case.grades_desc,
                               'annual_fees'  : case.annual_fees,
                               'sole_dsc'     : case.sole_dsc,
                               'sl_dsc_maker' : case.sl_dsc_maker,
                               'sl_dsign'     : case.sl_dsign,
                               'sl_contact'   : case.sl_contact,
                               'msc'          : case.msc,
                               'vec'          : case.vec,
                               'lssc'         : case.lssc,
                               'con'          : case.con,
                               'none'         : case.none,
                               'others'       : case.others,
                               'effec_med'    : case.effec_med,
                               'implement'    : case.implement,
                               'remks1'       : case.remks1,
                               'remks2'       : case.remks2,
                               'time_span'    : case.time_span,
                               'time_date'    : case.time_date,
                               'oth_days'     : case.oth_days,
                               'text1'        : case.text1,
                               'text2'        : case.text2,
                               'text3'        : case.text3,
                              })
        return {'value':data}
    
    # Overridden the standard case_close method
    def case_close(self, cr, uid, ids,*args):          
        res = {}
        models_data = self.pool.get('ir.model.data')
        mksale_obj = self.pool.get('crm.make.sale')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        cases = self.browse(cr, uid, ids)
        cases[0].state # to fill the browse record cache
        self._history(cr, uid, cases, _('Close'))   
        self.write(cr, uid, ids, {'state': 'done'})
        self._action(cr, uid, cases, 'done')
                
        for case in self.browse(cr, uid, ids):
            if not case.date_closed:
               self.write(cr, uid, ids, {'date_closed': time.strftime('%Y-%m-%d %H:%M:%S')})
            
            if case.type == 'lead':
                message = _("The lead '%s' has been closed.") % case.name
            elif case.type == 'opportunity':
                message = _("The opportunity '%s' has been closed.") % case.name 
            else:
                message = _("The case '%s' has been closed.") % case.name
            self.log(cr, uid, case.id, message)
            
            value = {}  
            stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Moved TO CRM'),('type','=','opportunity')])[0]                                    
            value.update({'stage_id' : stage_id})            
            self.write(cr, uid, ids, value)
            
            partner = case.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            
                
            if False in partner_addr.values():
                raise osv.except_osv(_('Data Insufficient!'), _('Customer has no addresses defined!'))

            vals = {
                'origin': _('Opportunity: %s') % str(case.id),
                'section_id': case.section_id and case.section_id.id or False,
               # 'shop_id': make.shop_id.id,
                'partner_id': partner.id,
                'pricelist_id': pricelist,
                'partner_invoice_id': partner_addr['invoice'],
                'partner_order_id': partner_addr['contact'],
                'partner_shipping_id': partner_addr['delivery'],
                'date_order': time.strftime('%Y-%m-%d'),
                'fiscal_position': fpos,
                'rsn_reject':case.rsn_reject,
                'ed_type':'so',
            }
            
            if partner.id:
                vals['user_id'] = partner.user_id and partner.user_id.id or uid
            new_id = sale_obj.create(cr, uid, vals)
            self.write(cr, uid, ids, {'ref': 'sale.order,%s' % new_id})            
            message = _('Opportunity ') + " '" + case.partner_id.name + "' "+ _("is converted to Quotation.")
            self.log(cr, uid, case.id, message)
            self._history(cr, uid, cases, _("Converted to Sales Quotation(id: %s).") % (new_id))
            
            view = models_data.get_object_reference(cr, uid, 'Edumedia_India', 'view_ed_sale_form')
            view_id = view and view[1] or False,
            
        return {
            'name': 'CRM And Proposal Order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': 'sale.order',
            'context': "{'default_ed_type':'so'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'old',
            'res_id': new_id and new_id or False,
        }  
    
     # Overridden the standard case_mark_lost method
    def case_mark_lost(self, cr, uid, ids, *args):

        res = self._case_close_generic(cr, uid, ids, self._find_lost_stage, *args)
        for case in self.browse(cr, uid, ids):
            message = _("The Lead '%s' has been marked as Cancelled.") % case.name
            self.log(cr, uid, case.id, message)
                 
        stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Rejected'),('type','=','opportunity')])[0]                                    
                    
        self.write(cr, uid, ids,{'state':'cancel','stage_id':stage_id})
            
        return res
    
    def case_reset(self, cr, uid, ids, *args):

        res = True
        stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Raw'),('type','=','opportunity')])[0]    
        self.write(cr, uid, ids, {'state':'draft', 'stage_id': stage_id, 'probability': 0.0})
        return res
    
    def case_pending(self, cr, uid, ids, *args):
       
        cases = self.browse(cr, uid, ids)
        cases[0].state # to fill the browse record cache
        self._history(cr, uid, cases, _('Pending'))
        stage_id = self.pool.get('crm.case.stage').search(cr,uid,[('name','=','Pipeline')])[0]
        self.write(cr, uid, ids, {'state': 'pending', 'stage_id': stage_id, 'active': True})
        self._action(cr, uid, cases, 'pending')
        return True     
    
    # Overriden: 
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
            
        if 'date_closed' in vals:
            return super(crm_lead,self).write(cr, uid, ids, vals, context=context)
            
        if 'stage_id' in vals and vals['stage_id']:
            stage_obj = self.pool.get('crm.case.stage').browse(cr, uid, vals['stage_id'], context=context) 
            message=''
            for case in self.browse(cr, uid, ids, context=context):
                if case.stage_id.id <> vals['stage_id']: 
                   self.history(cr, uid, ids, _('Stage'), details=stage_obj.name)
                   
                   if case.type == 'lead' or  context.get('stage_type',False) =='lead':
                        message = _("The stage of lead '%s' has been changed to '%s'.") % (case.name, stage_obj.name)
                   elif case.type == 'opportunity':
                        message = _("The stage of opportunity '%s' has been changed to '%s'.") % (case.name, stage_obj.name)
                   self.log(cr, uid, case.id, message)
        return super(osv.osv,self).write(cr, uid, ids, vals, context)
     
crm_lead()

class ed_channel_lines(osv.osv):
    _name='ed.channel.lines'
    _columns = {'lead_id':fields.many2one('crm.lead','Leads'),
                'channel_id':fields.many2one('ed.channel','Channel'),
                'remarks':fields.char('Remarks',size=128),
                }
ed_channel_lines()

class lead_qualification(osv.osv):
    _name='lead.qualification'
    
    def _get_points(self, cr, uid, ids, name, args, context=None):
        res = {}
                
        for case in self.browse(cr, uid, ids):
                res[case.id] = case.qparam_id and case.qparam_id.points or 0 
                                
        return res
    
    _columns={'lead_id':fields.many2one('crm.lead','Leads'),
              'qparam_id':fields.many2one('qualification.param','Qualification Parameter'),
              'type':fields.selection([('curriculum','Curriculum'),('schl_strength','School Strength'),('socio_eco','Socio Economic Background'),('time_span','Time Span')],'Type'),
              'points': fields.function(_get_points, method=True, string='Points',type='integer',store=True),
              }
lead_qualification()


    