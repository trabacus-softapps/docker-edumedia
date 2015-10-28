from openerp.osv import fields, osv
from openerp.tools.translate import _ 

class project_issue(osv.osv):
    _inherit = "project.issue"
    _columns = { 
                'ticket_no': fields.char('Ticket No.', size=100), 
                'ed_status_id' : fields.many2one('ed.ticket.status','Status'),
                'ed_date':fields.date('Deadline'),
                }
    
    
    # Need to replace in standard project_issue.py
    def _compute_day(self, cr, uid, ids, fields, args, context=None):
        """
        """
        cal_obj = self.pool.get('resource.calendar')
        res_obj = self.pool.get('resource.resource')

        res = {}
        for issue in self.browse(cr, uid, ids, context=context):
            for field in fields:
                res[issue.id] = {}
                duration = 0
                ans = False
                hours = 0

                if field in ['working_hours_open','day_open']:
                    if issue.date_open:
                        date_create = datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
                        date_open = datetime.strptime(issue.date_open, "%Y-%m-%d %H:%M:%S")
                        ans = date_open - date_create
                        date_until = issue.date_open
                        
                        #Calculating no. of working hours to open the issue
                        if issue.project_id and issue.project_id.resource_calendar_id:
                            hours = cal_obj.interval_hours_get(cr, uid, issue.project_id.resource_calendar_id.id,
                                     datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S'),
                                     datetime.strptime(issue.date_open, '%Y-%m-%d %H:%M:%S'))
                elif field in ['working_hours_close','day_close']:
                    if issue.date_closed:
                        date_create = datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
                        date_close = datetime.strptime(issue.date_closed, "%Y-%m-%d %H:%M:%S")
                        date_until = issue.date_closed
                        ans = date_close - date_create
                        
                        #Calculating no. of working hours to close the issue
                        if issue.project_id and issue.project_id.resource_calendar_id:
                            hours = cal_obj.interval_hours_get(cr, uid, issue.project_id.resource_calendar_id.id,
                                    datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S'),
                                    datetime.strptime(issue.date_closed, '%Y-%m-%d %H:%M:%S'))
                if ans:
                    resource_id = False
                    if issue.user_id:
                        resource_ids = res_obj.search(cr, uid, [('user_id','=',issue.user_id.id)])
                        if resource_ids and len(resource_ids):
                            resource_id = resource_ids[0]
                    duration = float(ans.days)
                    if issue.project_id and issue.project_id.resource_calendar_id:
                        duration = float(ans.days) * 24
                        new_dates = cal_obj.interval_min_get(cr, uid, issue.project_id.resource_calendar_id.id, datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S'), duration, resource=resource_id)
                        no_days = []
                        date_until = datetime.strptime(date_until, '%Y-%m-%d %H:%M:%S')
                        for in_time, out_time in new_dates:
                            if in_time.date not in no_days:
                                no_days.append(in_time.date)
                            if out_time > date_until:
                                break
                        duration = len(no_days)
                if field in ['working_hours_open','working_hours_close']:
                    res[issue.id][field] = hours
                else:
                    res[issue.id][field] = abs(float(duration))
        return res
    
project_issue()

class document_file(osv.osv):
    
    _inherit = 'ir.attachment'
    
    def __get_partner_id(self, cr, uid, res_model, res_id, context=None):
        """ A helper to retrieve the associated partner from any res_model+id
            It is a hack that will try to discover if the mentioned record is
            clearly associated with a partner record.
        """
        obj_model = self.pool.get(res_model)
        if obj_model._name == 'res.partner':
            return res_id
        elif 'partner_id' in obj_model._columns and obj_model._columns['partner_id']._obj == 'res.partner':
            bro = obj_model.browse(cr, uid, res_id, context=context)
            return bro.partner_id and bro.partner_id.id or False
        elif 'address_id' in obj_model._columns and obj_model._columns['address_id']._obj == 'res.partner':
            bro = obj_model.browse(cr, uid, res_id, context=context)
            return bro.address_id and bro.address_id.partner_id and bro.address_id.partner_id.id or False
        return False
    
document_file()
 