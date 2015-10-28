from openerp.osv import osv, fields
from openerp.tools.translate import _

class crm_partner2opportunity(osv.osv_memory):
    """Converts Partner To Opportunity"""

    _inherit = 'crm.lead2opportunity.partner'  
    _columns = {'serv_type':fields.selection([('School Cinema','School Cinema'),('Mentor','Mentor')
                                              ,('Krayon','Krayon'),('Activity','Activity')],'Service_Type',readonly=True),
                'salesman_id':fields.many2one('res.users','Salesman'),
                }
    _defaults={'serv_type':'School Cinema'
               }

    def default_get(self, cr, uid, fields, context=None):
        """
        
        """
#        partner_obj = self.pool.get('res.partner')
#        data = context and context.get('active_ids', []) or []
        res = super(crm_partner2opportunity, self).default_get(cr, uid, fields, context=context)

#        for partner in partner_obj.browse(cr, uid, data, []):
#            if 'name' in fields:
#                res.update({'name': partner.name})
#            if 'partner_id' in fields:
#                res.update({'partner_id': data and data[0] or False})
        res.update({'salesman_id':uid})
        return res


    def make_opportunity(self, cr, uid, ids, context=None):
        """ 
        """

        data = context and context.get('active_ids', []) or []
        make_opportunity = self.pool.get('crm.lead')
        
        for make_opportunity_obj in make_opportunity.browse(cr, uid, ids, context=context):
            data_obj = self.pool.get('ir.model.data')
            #result = data_obj._get_id(cr, uid, 'crm', 'view_crm_case_opportunities_filter')
            #res = data_obj.read(cr, uid, result, ['res_id'])
            lead_form = data_obj._get_id(
                              cr, uid, 'Edumedia_India', 'ed_crm_case_form_view_oppor')                  
            lead_tree = data_obj._get_id(
                              cr, uid, 'Edumedia_India', 'ed_crm_case_tree_view_oppor')
                 
            if lead_form:
                lead_form = data_obj.browse(
                                  cr, uid, lead_form, context=context).res_id
                   
            if lead_tree:
                lead_tree = data_obj.browse(
                                  cr, uid, lead_tree, context=context).res_id
            
#            id2 = data_obj._get_id(cr, uid,'ed_crm_case_form_view_oppor')
#            id3 = data_obj._get_id(cr, uid,'ed_crm_case_tree_view_oppor')
#            if id2:
#                id2 = data_obj.browse(cr, uid, id2, context=context).res_id
#            if id3:
#                id3 = data_obj.browse(cr, uid, id3, context=context).res_id

            part_obj = self.pool.get('res.partner')
#            address = part_obj.address_get(cr, uid, data)
#
#
#            categ_obj = self.pool.get('crm.case.categ')
#            categ_ids = categ_obj.search(cr, uid, [('object_id.model','=','crm.lead')])
#
#            case_obj = self.pool.get('crm.lead')
#            opp_id = case_obj.create(cr, uid, {
#                'name' : make_opportunity_obj.name,
#                'planned_revenue' : make_opportunity_obj.planned_revenue,
#                'probability' : make_opportunity_obj.probability,
#                'partner_id' : make_opportunity_obj.partner_id.id,
#                'partner_address_id' : address['default'],
#                'categ_id' : categ_ids and categ_ids[0] or '',
#                'state' :'draft',
#                'type': 'opportunity'
#            })
#            value = {
#                'name' : _('Opportunity'),
#                'view_type' : 'form',
#                'view_mode' : 'form,tree',
#                'res_model' : 'crm.lead',
#                'res_id' : opp_id,
#                'view_id' : False,
#                'views' : [(id2, 'form'), (id3, 'tree'), (False, 'calendar'), (False, 'graph')],
#                'type' : 'ir.actions.act_window',
#                'search_view_id' : res['res_id']
#            }
#            return value
            newopp = []
            case_obj = self.pool.get('crm.lead')
            for cust in data:
                address = part_obj.address_get(cr, uid, [cust])    
    
                categ_obj = self.pool.get('crm.case.categ')
                categ_ids = categ_obj.search(cr, uid, [('object_id.model','=','crm.lead')])
     
                opp_id = case_obj.create(cr, uid, {
                                   'name' :  part_obj.browse(cr, uid, cust).name,
                                    'email_from':part_obj.browse(cr, uid, cust).email,
                                    'phone':part_obj.browse(cr, uid, cust).phone,
                                    'planned_revenue' : make_opportunity_obj.planned_revenue,
                                    'probability' : make_opportunity_obj.probability,
                                    'partner_id' : cust,
                                    'partner_address_id' : address['default'],
                                    'categ_id' : categ_ids and categ_ids[0] or '',
                                    'state' :'draft',
                                    'type': 'opportunity',
                                    'user_id':make_opportunity_obj.salesman_id.id,
                }) 
                newopp.append(opp_id)
            
            res = data_obj.get_object_reference(cr, uid, 'crm', 'view_crm_case_opportunities_filter')
            return {'type': 'ir.actions.act_window_close'}
#            return {
#                'domain': "[('id','in', ["+','.join(map(str,newopp))+"])]",
#                'name':  _('Opportunity'),
#                'view_type': 'form',
#                'view_mode': 'tree,form',
#                'res_model' : 'crm.lead',
#                'view_id': False, 
#                'views'    : [(lead_tree, 'tree'),
#                            (lead_form, 'form'), ],
#                'type': 'ir.actions.act_window',
#                'search_view_id': res and res[1] or False
#            }
        
crm_partner2opportunity()        