from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
from dateutil.relativedelta import relativedelta

class MailActivity(models.Model):
    _inherit = "mail.activity"

    lxl_code = fields.Char(string="LXL CODE")

class Base(models.AbstractModel):
    _inherit = "base"

    def _get_default_lxl_stage(self):
        return self.lxl_stage_id.get_first_stage(self._name).id

    lxl_stage_id = fields.Many2one("res.stage",
                                   default=_get_default_lxl_stage,
                                   string="Stage",
                                   tracking=True)
    lxl_state = fields.Selection(string="State", related="lxl_stage_id.state")

    def _get_lxl_user_ids(self):
        if not self.lxl_stage_id.validation_by:
            return self.env.user.ids 
        if self.lxl_stage_id.validation_by == 'user':
            return self.lxl_stage_id.user_ids.ids
        elif self.lxl_stage_id.validation_by == 'group':
            return self.lxl_stage_id.group_ids.users.ids
        elif self.lxl_stage_id.validation_by == 'code':
            return eval(self.lxl_stage_id.python_code, {'self': self})
        return []

    @api.depends('lxl_stage_id')
    def _compute_lxl_is_active_user(self):
        for rec in self:
            user_ids = rec._get_lxl_user_ids()
            rec.lxl_is_active_user = rec.env.user.id in user_ids 

    lxl_is_active_user = fields.Boolean("res.users", compute=_compute_lxl_is_active_user)

    def next_stage(self):
        self.lxl_stage_id = self.lxl_stage_id.get_next_stage().id
        self.lxl_action_feedback()
        self.lxl_send_activity(self._get_lxl_user_ids(), message=f'New request of {self.lxl_stage_id.model_id.name} for approval')
        

    def prev_stage(self):
        self.lxl_stage_id = self.lxl_stage_id.get_prev_stage().id
        self.lxl_action_feedback()
        self.lxl_send_activity(self._get_lxl_user_ids(), message=f'Request of {self.lxl_stage_id.model_id.name} has been returned to you.')

    def first_stage(self):
        self.lxl_stage_id = self.lxl_stage_id.get_first_stage().id
        self.lxl_action_feedback()
        self.lxl_send_activity(self.create_uid.ids, message=f'Request of {self.lxl_stage_id.model_id.name} has been reset to draft.')

    def cancel_stage(self):
        self.lxl_stage_id = self.lxl_stage_id.get_cancel_stage().id

    def lxl_action_feedback(self):
        activity = self.env['mail.activity'].search([('lxl_code','=',f"{self._name}/{self.id}")])
        activity.action_feedback()

    def lxl_send_activity(self, users, message):
        for user in users:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'automated': True,
                'date_deadline': (fields.Datetime.today() + relativedelta(days=5)).strftime('%Y-%m-%d %H:%M'),
                'summary': message,
                'note': self.display_name,
                'user_id': user,
                'res_id': self.id,
                'lxl_code': f"{self._name}/{self.id}",
                'res_model_id': self.lxl_stage_id.model_id.id,
            })
        
    
    def run_lxl_action(self):
        action = self._context.get('lxl_action')
        actions = action.split(',')
        if actions:
            for action in actions:
                if action:
                    getattr(self, action)()
                else:
                    raise ValidationError(_("Action %s not found")%(action))
                
    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        if res.get('views',{}).get('form',{}) and self.env['res.stage'].search_count([('res_model','=', self._name)]):
            arch = res.get('views',{}).get('form',{}).get('arch', '')
            arch = etree.fromstring(arch)
            header = self._get_lxl_stage_extention_view()
            form = arch.xpath('/form')
            if form:
                existing_header = form[0].xpath('//form/header')
                if existing_header:
                    existing_header[0].set('invisible', '1')
                form[0].insert(0, etree.fromstring(header))
            res["views"]["form"]["arch"] = etree.tostring(arch).decode()
        return res
    

    def _get_lxl_stage_extention_view(self):
        buttons = []
        for button in self.lxl_stage_id.search([('res_model','=', self._name)]).action_ids.sorted('sequence'):
            if button.stage_id.state == 'first' and not button.stage_id.validation_by:
                if button.stage_id.action_create_user:
                    attr = f"""invisible='lxl_stage_id != {button.stage_id.id} or create_uid != {self.env.user.id}'"""
                else:
                    attr = f"""invisible='lxl_stage_id != {button.stage_id.id}'"""
            else:
                attr = f"""invisible='lxl_stage_id != {button.stage_id.id} or lxl_is_active_user == False'"""
            buttons += [f"""<button name="{button.action}" 
                            string="{button.name}"
                            class="{button.get_css_calss()}"
                            {attr}
                            type='object'/>"""]    
        view = f"""
            <header>
                {' '.join(buttons)}
                <field name="lxl_stage_id" widget="statusbar" domain="[('res_model','=', '{self._name}'),('state','!=','cancel')]"/>
                <field name="lxl_is_active_user" invisible="1"/>
                <field name="create_uid" invisible="1"/>
            </header>
        """
        return view