from openerp.osv import fields, osv
from dateutil import parser
import re
import calendar
import openerp.tools
import openerp.addons.decimal_precision as dp
import amount_to_text_softapps

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from openerp.addons.hr_payroll import hr_payroll

class hr_payroll_register(osv.osv):
    _name = 'hr.payroll.register'
    _description = 'Payroll Register'
    _columns = {'annual':fields.boolean('Annual payments')}
    
hr_payroll_register()

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    
    def _calculate(self, cr, uid, ids, field_names, arg, context=None):
        
        res = super(hr_payslip, self)._calculate(cr, uid, ids,field_names,context)
        for case in self.browse(cr,uid,ids):
            res[case.id]['total_pay'] = res[case.id]['other_pay'] + res[case.id]['net'] 
            if res[case.id]['total_pay'] >= 0 :
                res[case.id]['amt_words'] = ' Rupees ' + amount_to_text_softapps._100000000_to_text(int(round(res[case.id]['total_pay']))) + ' Only' 
        return res
    
    _columns = {'paid_lv':fields.float('Paid Leaves'),
                'unpaid_lv':fields.float('UnPaid Leaves'),
                'grows': fields.function(_calculate, method=True, store=True, multi='dc', string='Gross Salary', digits_compute=dp.get_precision('Account')),
                'net': fields.function(_calculate, method=True, store=True, multi='dc', string='Net Salary', digits_compute=dp.get_precision('Account')),
                'allounce': fields.function(_calculate, method=True, store=True, multi='dc', string='Allowance', digits_compute=dp.get_precision('Account')),
                'deduction': fields.function(_calculate, method=True, store=True, multi='dc', string='Deduction', digits_compute=dp.get_precision('Account')),
                'other_pay': fields.function(_calculate, method=True, store=True, multi='dc', string='Others', digits_compute=dp.get_precision('Account')),
                'total_pay': fields.function(_calculate, method=True, store=True, multi='dc', string='Total Payment', digits_compute=dp.get_precision('Account')),
                'amt_words': fields.function(_calculate, method=True, multi='dc', string="Amount in Words", type='text'),
                'journal_id': fields.many2one('account.journal', 'Expense Journal',readonly=True, states={'draft': [('readonly', False)]}),
                'bank_journal_id': fields.many2one('account.journal', 'Bank Journal',readonly=True, states={'draft': [('readonly', False)]}),
                'line_ids':fields.one2many('hr.payslip.line', 'slip_id', 'Payslip Line', required=False, readonly=True, states={'draft': [('readonly', False)]}),

                }
   # _order = 'date desc'
    
#    def compute_sheet(self, cr, uid, ids, context=None):
#        atten_obj = self.pool.get('hr.attendance')
#        cont_obj = self.pool.get('hr.contract')
#        pay_line_obj = self.pool.get('hr.payslip.line')
#        holstat_obj = self.pool.get('hr.holidays.status')
#        payreg_obj = self.pool.get('hr.payroll.register')
#        salhead_obj = self.pool.get('hr.allounce.deduction.categoty')
#        resval={}
#        pln_ids = [] 
#        wrkedays = paiday = unpaiday = leave_ded = 0
#        res = super(hr_payslip, self).compute_sheet(cr, uid, ids,context)
#        
#        for case in self.browse(cr,uid,ids):
#            if case.register_id and case.line_ids:
##                val = payreg_obj.browse(cr,uid,case.register_id.id).annual
##                val = 
##                if not case.register_id.annual:
##                   salhead_ids = salhead_obj.search(cr,uid,[('annual','=',True)])
##                   for sl in salhead_ids:
##                       payln_ids  = pay_line_obj.search(cr,uid,[('category_id','=',sl),('slip_id','=',case.id)])
##                       pay_line_obj.unlink(cr,uid,payln_ids)
#                holstat_id = holstat_obj.search(cr,uid,[('type','=','unpaid')], limit=1)
#                salhd_id = holstat_obj.browse(cr,uid,holstat_id)
#                
#                if salhd_id.head_id.id:
#                    pln_ids = pay_line_obj.search(cr,uid,[('category_id','=',salhd_id.head_id.id),('slip_id','=',case.id)],limit=1)
#                
#            pay_slip_date = ((parser.parse(''.join((re.compile('\d')).findall(case.date))))).strftime("%Y-%m-%d")
#            total_sal = case.basic + case.allounce
#            mon = ((parser.parse(''.join((re.compile('\d')).findall(case.date))))).strftime("%m")
#
#            cr.execute("""select id,state 
#                                 from ed_attendance 
#                                 where extract(MONTH from log_date ::date) = '%s' 
#                                 and employee_id = %d 
#                                 """%(mon,case.employee_id))        
#            all_days = cr.dictfetchall()
#            for d in all_days:
#                if d['state'] in('present','paid','holiday','time_off'):
#                    wrkedays += 1
#                if d['state'] == 'paid':
#                    paiday += 1    
#                if d['state'] == 'unpaid':
#                    unpaiday += 1
#            resval['worked_days'] = wrkedays
#            resval['paid_lv'] = paiday 
#            resval['unpaid_lv'] = unpaiday
#            if total_sal and case.working_days:
#               leave_ded = (total_sal/case.working_days) * unpaiday
#            resval['leaves'] = leave_ded
#            pay_line_obj.write(cr,uid,pln_ids,{'amount':leave_ded})
#            self.write(cr,uid,ids,resval)            
#            return res


    def compute_sheet(self, cr, uid, ids, context=None):
        func_pool = self.pool.get('hr.payroll.structure')
        slip_line_pool = self.pool.get('hr.payslip.line')
        holiday_pool = self.pool.get('hr.holidays')
        sequence_obj = self.pool.get('ir.sequence')
        salhead_obj = self.pool.get('hr.allounce.deduction.categoty')        
        holstat_obj = self.pool.get('hr.holidays.status')
        payreg_obj = self.pool.get('hr.payroll.register')
        category_ids = salhead_obj.search(cr,uid,[('annual','=',True)])
        
        if context is None:
            context = {}
        date = self.read(cr, uid, ids, ['date'], context=context)[0]['date']

        #Check for the Holidays
        def get_days(start, end, month, year, calc_day):
            import datetime
            count = 0
            for day in range(start, end):
                if datetime.date(year, month, day).weekday() == calc_day:
                    count += 1
            return count

        for slip in self.browse(cr, uid, ids, context=context):
            old_slip_ids = slip_line_pool.search(cr, uid, [('slip_id','=',slip.id)], context=context)
            slip_line_pool.unlink(cr, uid, old_slip_ids, context=context)
            update = {}
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(slip.date,"%Y-%m-%d")))
            contracts = self.get_contract(cr, uid, slip.employee_id, date, context)
            if contracts.get('id', False) == False:
                update.update({
                    'basic': round(0.0),
                    'basic_before_leaves': round(0.0),
                    'name':'Salary Slip of %s for %s' % (slip.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'state':'draft',
                    'contract_id':False,
                    'company_id':slip.employee_id.company_id.id
                })
                self.write(cr, uid, [slip.id], update, context=context)
                continue

            contract = slip.employee_id.contract_id
            sal_type = contract.wage_type_id.type
            function = contract.struct_id.id
            lines = []
            if function:
                func = func_pool.read(cr, uid, function, ['line_ids'], context=context)      
                print "before", func       
                print 'annual',slip.register_id.annual
                if not slip.register_id.annual:
                   sliplnids = slip_line_pool.search(cr, uid, [('function_id','=', function), ('category_id','in', category_ids)])
                   for sl in sliplnids:
                       func['line_ids'].remove(sl)               
                lines = slip_line_pool.browse(cr, uid, func['line_ids'], context=context) 
                print "after", func  

            #lines += slip.employee_id.line_ids

            ad = []
            all_per = ded_per = all_fix = ded_fix = 0.0

            obj = {'basic':0.0}
            if contract.wage_type_id.type == 'gross':
                obj['gross'] = contract.wage
                update['igross'] = contract.wage
            if contract.wage_type_id.type == 'net':
                obj['net'] = contract.wage
                update['inet'] = contract.wage
            if contract.wage_type_id.type == 'basic':
                obj['basic'] = contract.wage
                update['basic'] = contract.wage

            for line in lines:
                cd = line.code.lower()
                obj[cd] = line.amount or 0.0

            for line in lines:
                if line.category_id.code in ad:
                    continue
                ad.append(line.category_id.code)
                cd = line.category_id.code.lower()
                calculate = False
                try:
                    exp = line.category_id.condition
                    calculate = eval(exp, obj)
                except Exception, e:
                    raise osv.except_osv(_('Variable Error !'), _('Variable Error: %s ') % (e))

                if not calculate:
                    continue

                percent = value = 0.0
                base = False
#                company_contrib = 0.0
                base = line.category_id.base

                try:
                    #Please have a look at the configuration guide.
                    amt = eval(base, obj)
                except Exception, e:
                    raise osv.except_osv(_('Variable Error !'), _('Variable Error: %s ') % (e))

                if sal_type in ('gross', 'net'):
                    if line.amount_type == 'per':
                        percent = line.amount
                        if amt > 1:
                            value = percent * amt
                        elif amt > 0 and amt <= 1:
                            percent = percent * amt
                        if value > 0:
                            percent = 0.0
                    elif line.amount_type == 'fix':
                        value = line.amount
                    elif line.amount_type == 'func':
                        value = slip_line_pool.execute_function(cr, uid, line.id, amt, context)
                        line.amount = value
                else:
                    if line.amount_type in ('fix', 'per'):
                        value = line.amount
                    elif line.amount_type == 'func':
                        value = slip_line_pool.execute_function(cr, uid, line.id, amt, context)
                        line.amount = value
                if line.type == 'allowance':
                    all_per += percent
                    all_fix += value
                elif line.type == 'deduction':
                    ded_per += percent
                    ded_fix += value
                vals = {
                    'amount':line.amount,
                    'slip_id':slip.id,
                    'employee_id':False,
                    'function_id':False,
                    'base':base
                }
                slip_line_pool.copy(cr, uid, line.id, vals, {})
            if sal_type in ('gross', 'net'):
                sal = contract.wage
                if sal_type == 'net':
                    sal += ded_fix
                sal -= all_fix
                per = 0.0
                if sal_type == 'net':
                    per = (all_per - ded_per)
                else:
                    per = all_per
                if per <=0:
                    per *= -1
                final = (per * 100) + 100
                basic = (sal * 100) / final
            else:
                basic = contract.wage

            number = sequence_obj.get(cr, uid, 'salary.slip')
            update.update({
                'deg_id':function,
                'number':number,
                'basic': round(basic),
                'basic_before_leaves': round(basic),
                'name':'Salary Slip of %s for %s' % (slip.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                'state':'draft',
                'contract_id':contract.id,
                'company_id':slip.employee_id.company_id.id
            })

            for line in slip.employee_id.line_ids:
                vals = {
                    'amount':line.amount,
                    'slip_id':slip.id,
                    'employee_id':False,
                    'function_id':False,
                    'base':base
                }
                slip_line_pool.copy(cr, uid, line.id, vals, {})

            self.write(cr, uid, [slip.id], update, context=context)

        for slip in self.browse(cr, uid, ids, context=context):
            if not slip.contract_id:
                continue

            basic_before_leaves = slip.basic
            working_day = 0
            off_days = 0
            dates = hr_payroll.prev_bounds(slip.date)

            days_arr = [0, 1, 2, 3, 4, 5, 6]
            for dy in range(slip.employee_id.contract_id.working_days_per_week, 7):
                off_days += get_days(1, dates[1].day, dates[1].month, dates[1].year, days_arr[dy])
            total_off = off_days
            working_day = dates[1].day - total_off
            perday = slip.net / working_day
            total = 0.0
            leave = 0.0
            leave_ids = self._get_leaves(cr, uid, slip, slip.employee_id, context)
            total_leave = 0.0
            paid_leave = 0.0
            for hday in holiday_pool.browse(cr, uid, leave_ids, context=context):
                if not hday.holiday_status_id.head_id:
                    raise osv.except_osv(_('Error !'), _('Please check configuration of %s, payroll head is missing') % (hday.holiday_status_id.name))

                res = {
                    'slip_id':slip.id,
                    'name':hday.holiday_status_id.name + '-%s' % (hday.number_of_days),
                    'code':hday.holiday_status_id.code,
                    'amount_type':'fix',
                    'category_id':hday.holiday_status_id.head_id.id,
                    'sequence':hday.holiday_status_id.head_id.sequence
                }
                days = hday.number_of_days
                if hday.number_of_days < 0:
                    days = hday.number_of_days * -1
                total_leave += days
                if hday.holiday_status_id.type == 'paid':
                    paid_leave += days
                    continue
#                    res['name'] = hday.holiday_status_id.name + '-%s' % (days)
#                    res['amount'] = perday * days
#                    res['type'] = 'allowance'
#                    leave += days
#                    total += perday * days

                elif hday.holiday_status_id.type == 'halfpaid':
                    paid_leave += (days / 2)
                    res['name'] = hday.holiday_status_id.name + '-%s/2' % (days)
                    res['amount'] = perday * (days/2)
                    total += perday * (days/2)
                    leave += days / 2
                    res['type'] = 'deduction'
                else:
                    res['name'] = hday.holiday_status_id.name + '-%s' % (days)
                    res['amount'] = perday * days
                    res['type'] = 'deduction'
                    leave += days
                    total += perday * days

                slip_line_pool.create(cr, uid, res, context=context)
            basic = basic - total
#            leaves = total
            
            update.update({
                'basic':basic,
                'basic_before_leaves': round(basic_before_leaves),
                'leaves':total,
                'holiday_days':leave,
                'worked_days':working_day - leave,
                'working_days':working_day,
            })
            
            holstat_id = holstat_obj.search(cr,uid,[('type','=','unpaid')], limit=1)
            if holstat_id:
                salhd_id = holstat_obj.browse(cr,uid,holstat_id[0])
            
                pln_ids = slip_line_pool.search(cr,uid,[('category_id','=',salhd_id.head_id.id),('slip_id','=',slip.id)],limit=1)
                
            pay_slip_date = ((parser.parse(''.join((re.compile('\d')).findall(slip.date))))).strftime("%Y-%m-%d")
            total_sal = slip.basic + slip.allounce
            mon = ((parser.parse(''.join((re.compile('\d')).findall(slip.date))))).strftime("%m")

            cr.execute("""select id,state,no_days 
                                 from ed_attendance 
                                 where extract(MONTH from log_date ::date) = '%s' 
                                 and employee_id = %d 
                                 """%(mon,slip.employee_id))        
            all_days = cr.dictfetchall()
            wrkedays = paiday = unpaiday = leave_ded = 0
            for d in all_days:
                if d['state'] in('present','paid','holiday','time_off'):
                    wrkedays += d['no_days']
                if d['state'] == 'paid':
                    paiday += d['no_days']    
                if d['state'] == 'unpaid':
                    unpaiday += d['no_days']
            update['worked_days'] = wrkedays
            update['paid_lv'] = paiday 
            update['unpaid_lv'] = unpaiday
            if total_sal and slip.working_days:
               leave_ded = (total_sal/slip.working_days) * unpaiday
            update['leaves'] = leave_ded
            slip_line_pool.write(cr,uid,pln_ids,{'amount':leave_ded})
            self.write(cr, uid, [slip.id], update, context=context)
            
        return True
    
hr_payslip() 

class payment_category(osv.osv):
    _name = 'hr.allounce.deduction.categoty'
    _description = 'Allowance Deduction Heads'
    _columns = {'annual':fields.boolean('Annual Payments')}
payment_category()