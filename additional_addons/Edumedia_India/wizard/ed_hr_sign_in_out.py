from openerp.osv import fields,osv
import time


class  hr_sign_in_out(osv.osv_memory):
    
    _name = 'hr.sign.in.out'
    _description = 'Sign In Sign Out'
    
    _columns = {
        'name': fields.char('Employees name', size=32, required=True, readonly=True),
        'state': fields.char('Current state', size=32, required=True, readonly=True),
        'emp_id': fields.char('Employee ID', size=32, required=True, readonly=True),
                }
    
    def _get_empid(self, cr, uid, context=None):
        emp_id = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if emp_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, emp_id, context=context)[0]
            return {'name': employee.name, 'state': employee.state, 'emp_id': emp_id[0]}
        return {}

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(hr_sign_in_out, self).default_get(cr, uid, fields_list, context=context)
        res_emp = self._get_empid(cr, uid, context=context)
        res.update(res_emp)
        return res

    def si_check(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        att_obj = self.pool.get('hr.attendance')
        data = self.read(cr, uid, ids, [], context=context)[0]
        emp_id = data['emp_id']
        att_id = att_obj.search(cr, uid, [('employee_id', '=', emp_id)], limit=1, order='name desc')
        last_att = att_obj.browse(cr, uid, att_id, context=context)
        if last_att:
            last_att = last_att[0]
        cond = not last_att or last_att.action == 'sign_out'
        if cond:
            return self.sign_in(cr, uid, data, context)
        else:
            model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_hr_attendance_so_ask')], context=context)
            resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
            return {
                'name': _('Sign in / Sign out'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.sign.in.out.ask',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def so_check(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        att_obj = self.pool.get('hr.attendance')
        data = self.read(cr, uid, ids, [], context=context)[0]
        emp_id = data['emp_id']
        att_id = att_obj.search(cr, uid, [('employee_id', '=', emp_id),('action', '!=', 'action'),('day','=',time.strftime("%Y-%m-%d"))], limit=1, order='name desc')
        last_att = att_obj.browse(cr, uid, att_id, context=context)
        if last_att:
            last_att = last_att[0]
        if not att_id and not last_att:
            model_data_ids = obj_model.search(cr, uid, [('model','=','ir.ui.view'),('name','=','view_hr_attendance_message')], context=context)
            resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
            return {
                'name': _('Sign in / Sign out'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.sign.in.out',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

        cond = last_att and last_att['action'] == 'sign_in'
        if cond:
            return self.sign_out(cr, uid, data, context)
        else:
            model_data_ids = obj_model.search(cr, uid, [('model','=','ir.ui.view'),('name','=','view_hr_attendance_si_ask')], context=context)
            resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
            return {
                'name': _('Sign in / Sign out'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.sign.in.out.ask',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def sign_in(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        emp_id = data['emp_id']
        if 'last_time' in data:
            if data['last_time'] > time.strftime('%Y-%m-%d %H:%M:%S'):
                raise osv.except_osv(_('UserError'), _('The sign-out date must be in the past'))
            self.pool.get('hr.attendance').create(cr, uid, {'name': data['last_time'], 'action': 'sign_out',
                'employee_id': emp_id}, context=context)
        try:
            self.pool.get('hr.employee').attendance_action_change(cr, uid, [emp_id], 'sign_in')
        except:
            raise osv.except_osv(_('UserError'), _('A sign-in must be right after a sign-out !'))
        return {'type': 'ir.actions.act_window_close'} # To do: Return Success message

    def sign_out(self, cr, uid, data, context=None):
        emp_id = data['emp_id']
        if 'last_time' in data:
            if data['last_time'] > time.strftime('%Y-%m-%d %H:%M:%S'):
                raise osv.except_osv(_('UserError'), _('The Sign-in date must be in the past'))
            self.pool.get('hr.attendance').create(cr, uid, {'name':data['last_time'], 'action':'sign_in',  'employee_id':emp_id}, context=context)
        try:
            self.pool.get('hr.employee').attendance_action_change(cr, uid, [emp_id], 'sign_out')
        except:
            raise osv.except_osv(_('UserError'), _('A sign-out must be right after a sign-in !'))
        return {'type': 'ir.actions.act_window_close'} # To do: Return Success message

 # cutomised
    
    def check_sign_in(self,cr,uid,ids,context=None):
        obj_model = self.pool.get('ir.model.data') 
        att_obj = self.pool.get('hr.attendance')
        Emp_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids, [], context=context)[0]
        emp_id = data['emp_id']
        att_id = att_obj.search(cr, uid, [('employee_id', '=', emp_id),('day','=',time.strftime("%Y-%m-%d"))], limit=1, order='name desc')
        last_att = att_obj.browse(cr, uid, att_id, context=context)
        if last_att:
            last_att = last_att[0]
        cond = not last_att or last_att.action == 'sign_out'
        if cond:
             att_obj.create(cr,uid,{'action':'sign_in',
                                    'employee_id':emp_id,
                                    'name': time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'day': time.strftime("%Y-%m-%d"),
                                    'validated_ok':False})
        
        emp = Emp_obj.browse(cr,uid,emp_id)
        reqst_obj = self.pool.get('res.request')
        
        req_ids = []
        vals = { 
                'name': 'Log IN/OUT Status'
               ,'act_to': emp.manager_id and emp.manager_id.user_id and emp.manager_id.user_id.id or False
               ,'body':'Employee ' + str(emp.name) + ' has Signed In. '
               ,'priority':'2'
                } 
        if vals['act_to']:
            req_id = reqst_obj.create(cr, uid, vals)
            req_ids.append(req_id)
        
        vals['act_to'] = emp.manager2_id and emp.manager2_id.user_id and emp.manager2_id.user_id.id or False
        if vals['act_to']:
           req_id = reqst_obj.create(cr, uid, vals)
           req_ids.append(req_id)
                   
        vals['act_to'] = emp.manager3_id and emp.manager3_id.user_id and emp.manager3_id.user_id.id or False
        if vals['act_to']:            
           req_id = reqst_obj.create(cr, uid, vals)
           req_ids.append(req_id)
        
        reqst_obj.request_send(cr, uid, req_ids)            
        
        return {'type': 'ir.actions.act_window_close'}
  
    def check_sign_out(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        att_obj = self.pool.get('hr.attendance')
        Emp_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids, [], context=context)[0]
        emp_id = data['emp_id']
        att_id = att_obj.search(cr, uid, [('employee_id', '=', emp_id),('action', '!=', 'action'),('day','=',time.strftime("%Y-%m-%d"))], limit=1, order='name desc')
        last_att = att_obj.browse(cr, uid, att_id, context=context)
        if last_att:
            last_att = last_att[0]
        if not att_id and not last_att:
           raise osv.except_osv(_('Warning !'),_('Sign Out must happen Right after Sign in!!!')) 

        cond = last_att and last_att['action'] == 'sign_in'
        if cond:
            att_obj.create(cr,uid,{'action':'sign_out',
                                    'employee_id':emp_id,
                                    'name': time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'day': time.strftime("%Y-%m-%d"),
                                    'validated_ok':False})
        else:
           raise osv.except_osv(_('Warning !'),_('Sign Out must happen Right after Sign in!!!')) 
       
        emp = Emp_obj.browse(cr,uid,emp_id)
        reqst_obj = self.pool.get('res.request')
        
        req_ids = []
        vals = { 
                'name': 'Log IN/OUT Status'
               ,'act_to': emp.manager_id and emp.manager_id.user_id and emp.manager_id.user_id.id or False
               ,'body':'Employee ' + str(emp.name) + ' has Signed Out.'
               ,'priority':'2'
                } 
        if vals['act_to']:
           req_id = reqst_obj.create(cr, uid, vals)
           req_ids.append(req_id)
        
        vals['act_to'] = emp.manager2_id and emp.manager2_id.user_id and emp.manager2_id.user_id.id or False
        if vals['act_to']:
           req_id = reqst_obj.create(cr, uid, vals)
           req_ids.append(req_id)
        
        vals['act_to'] = emp.manager3_id and emp.manager3_id.user_id and emp.manager3_id.user_id.id or False
        if vals['act_to']:
           req_id = reqst_obj.create(cr, uid, vals)
           req_ids.append(req_id)
        
        reqst_obj.request_send(cr, uid, req_ids)
    
        return {'type': 'ir.actions.act_window_close'}
    
hr_sign_in_out()           