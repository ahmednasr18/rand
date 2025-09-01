from odoo import models, fields, api
from lxml import etree, html
import json

class ResStage(models.Model):
    _name = "res.stage"

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    _state = [('first', 'First'),
              ('middle', 'Middle'),
              ('end', 'End'),
              ('cancel', 'Cancel')]
    
    state = fields.Selection(_state,
                             default=_state[0][0], 
                             string="State")

    action_create_user = fields.Boolean(string="Display action for only create user", default=True)

    @api.onchange('state')
    def onchange_state(self):
        self.action_ids = False
        actions = False
        if self.state == 'first':
            actions = [[0,0,{
                'name': 'Send',
                'class_name': 'primary',
                'action': 'next_stage'
            }]]
        elif self.state == 'middle':
            actions = [[0,0,{
                'name': 'Accept',
                'class_name': 'primary',
                'action': 'next_stage'
            }],[0,0,{
                'name': 'Back to previous stage',
                'class_name': 'secondary',
                'action': 'prev_stage'
            }],[0,0,{
                'name': 'Cancel',
                'class_name': 'danger',
                'action': 'cancel_stage'
            }],[0,0,{
                'name': 'Reset To Draft',
                'class_name': 'secondary',
                'action': 'first_stage'
            }]]
        elif self.state == 'cancel':
            actions = [[0,0,{
                'name': 'Reset To Draft',
                'class_name': 'secondary',
                'action': 'first_stage'
            }]]
        self.action_ids = actions

    action_ids = fields.One2many('res.stage.action',
                                 'stage_id',
                                 string="Actions")
    
    sequence = fields.Integer(string="Sequence")

    description = fields.Text(string="Description")

    model_id = fields.Many2one('ir.model',string="Model")

    res_model = fields.Char(string="Model", related="model_id.model", store=True)

    _validation_by = [('user','User'),
                      ('group','Group'),
                      ('code', 'Code')]

    validation_by = fields.Selection(_validation_by, string="Validation By")

    user_ids = fields.Many2many("res.users",string="Users")
    group_ids = fields.Many2many("res.groups",string="Users")

    python_code = fields.Text(string="Code")


    def get_next_stage(self):
        stage = self.search([('model_id','=', self.model_id.id),
                             ('sequence','>', self.sequence)], 
                             order="sequence asc", 
                             limit=1)
        if not stage:
            stage = self
        return stage
    
    def get_prev_stage(self):
        stage = self.search([('model_id','=', self.model_id.id),
                             ('sequence','<', self.sequence)], 
                             order="sequence desc", 
                             limit=1)
        if not stage:
            stage = self
        return stage
    
    def get_first_stage(self, model=False):
        stage = self.search([('model_id','=', model if model else self.model_id.id),
                             ('state','=', 'first')],  
                             limit=1)
        return stage
    
    def get_cancel_stage(self):
        stage = self.search([('model_id','=', self.model_id.id),
                             ('state','=', 'cancel')],  
                             limit=1)
        return stage