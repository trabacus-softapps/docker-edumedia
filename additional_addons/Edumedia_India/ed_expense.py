from openerp.osv import fields,osv 

class hr_expense_expense(osv.osv): 
    _inherit='hr.expense.expense' 
    _columns = {
                  'manager_id': fields.related('employee_id','manager_id',relation='hr.employee', string='Manager', type='many2one', store=True,readonly=True, states={'draft':[('readonly',False)]}),
                  'employee_id': fields.many2one('hr.employee', "Employee"),
                  'name': fields.char('Description', size=128, required=True,readonly=True, states={'draft':[('readonly',False)]}),
                  'ref': fields.char('Reference', size=32,readonly=True, states={'draft':[('readonly',False)]}),
                  'date': fields.date('Date', select=True,readonly=True, states={'draft':[('readonly',False)]}),
                  'department_id':fields.many2one('hr.department','Department',readonly=True, states={'draft':[('readonly',False)]} ),
                  'company_id': fields.many2one('res.company', 'Company', required=True,readonly=True, states={'draft':[('readonly',False)]} ),  
                  'currency_id': fields.many2one('res.currency', 'Currency', required=True,readonly=True, states={'draft':[('readonly',False)]}),
                  'line_ids': fields.one2many('hr.expense.line', 'expense_id', 'Expense Lines', readonly=True, states={'draft':[('readonly',False)]}),
                  'journal_id': fields.many2one('account.journal', 'Force Journal', help = "The journal used when the expense is invoiced",readonly=True, states={'draft':[('readonly',False)]}),
                  'invoice_id': fields.many2one('account.invoice', "Employee's Invoice",readonly=True, states={'draft':[('readonly',False)]}),
                  'user_valid': fields.many2one('res.users', 'Validation User',readonly=True, states={'draft':[('readonly',False)]}),
               } 
    _order = 'date desc'
    def button_ed_draft(self, cr, uid, ids, *args):
        self.write(cr,uid,ids,{'state':'draft'})
        return True
    
    def expense_confirm(self, cr, uid, ids, *args):
        reqst_obj = self.pool.get('res.request')
        res = super(hr_expense_expense, self).expense_confirm(cr, uid, ids)
        for case in self.browse(cr,uid,ids):
            req_ids = []
            vals = { 
                    'name': 'Expense Request'
                   ,'act_to': case.employee_id.manager_id and case.employee_id.manager_id.user_id and case.employee_id.manager_id.user_id.id or False
                   ,'body':'Employee ' + str(case.employee_id.name) + ' has applied for expense. '
                            'Please do the needful' 
                   ,'priority':'2'
                    } 
            if vals['act_to']:
                req_id = reqst_obj.create(cr, uid, vals)
                req_ids.append(req_id)
            
            vals['act_to'] = case.employee_id.manager2_id and case.employee_id.manager2_id.user_id and case.employee_id.manager2_id.user_id.id or False
            if vals['act_to']:
                req_id = reqst_obj.create(cr, uid, vals)
                req_ids.append(req_id)
            
            vals['act_to'] = case.employee_id.manager3_id and case.employee_id.manager3_id.user_id and case.employee_id.manager3_id.user_id.id or False
            if vals['act_to']:
                req_id = reqst_obj.create(cr, uid, vals)
                req_ids.append(req_id)
            
            reqst_obj.request_send(cr, uid, req_ids)
        return res
    
    def expense_accept(self, cr, uid, ids, *args):    
        reqst_obj = self.pool.get('res.request')
        user_obj = self.pool.get('res.users')
        res = super(hr_expense_expense, self).expense_accept(cr, uid, ids)
        for case in self.browse(cr,uid,ids):
            man_name = user_obj.browse(cr,uid,uid).name
            
            if case.employee_id.user_id:
                vals = { 
                        'name': 'Expense Request'
                       ,'act_to': case.employee_id.user_id.id
                       ,'body':'Manager ' + str(man_name or '') + ' has approved your expense. '
                       ,'priority':'2'
                        } 
                req_id = reqst_obj.create(cr, uid, vals)
                reqst_obj.request_send(cr, uid, [req_id])
        return res
    
    def expense_canceled(self, cr, uid, ids, *args):
        reqst_obj = self.pool.get('res.request')
        user_obj = self.pool.get('res.users')
        res = super(hr_expense_expense, self).expense_canceled(cr, uid, ids)
        for case in self.browse(cr,uid,ids):
            man_name = user_obj.browse(cr,uid,uid).name
            
            if case.employee_id.user_id:
                vals = { 
                        'name': 'Expense Request'
                       ,'act_to': case.employee_id.user_id.id
                       ,'body':'Manager ' + str(man_name or '') + ' has refused your expense. '
                       ,'priority':'2'
                        } 
                req_id = reqst_obj.create(cr, uid, vals)
                reqst_obj.request_send(cr, uid, [req_id])
        return res
    
hr_expense_expense()