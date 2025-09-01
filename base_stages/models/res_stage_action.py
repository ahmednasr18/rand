from odoo import models, fields, api
from lxml import etree, html
import json

class ResStageAction(models.Model):
    _name = "res.stage.action"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")

    _class_name = [
        ('primary','Primary'),
        ('secondary','Secondary'),
        ('warning','Warning'),
        ('danger','Danger')
    ]
    
    class_name = fields.Selection(_class_name, 
                             default=_class_name[0][0],
                             string="Class Name")
    
    action = fields.Char(string="Action")

    stage_id = fields.Many2one('res.stage', string="Stage")

    def get_css_calss(self):
        css_class = {'primary': 'btn btn-primary',
                     'secondary': 'btn btn-secondary',
                     'warning': 'btn btn-warning',
                     'danger': 'btn btn-danger'}
        return css_class.get(self.class_name, 'btn btn-secondary')