# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cost_readonly = fields.Boolean(compute='_compute_cost_readonly')

    def _compute_cost_readonly(self):
        user = self.env.user
        for rec in self:
            if user.has_group("sha_pro_cost_access.group_access_product_cost"):
                rec.cost_readonly = True
            else:
                rec.cost_readonly = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    cost_readonly = fields.Boolean(compute='_compute_cost_readonly')

    def _compute_cost_readonly(self):
        user = self.env.user
        for rec in self:
            if user.has_group("sha_pro_cost_access.group_access_product_cost"):
                rec.cost_readonly = True
            else:
                rec.cost_readonly = False


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cost_readonly = fields.Boolean(compute='_compute_cost_readonly')

    def _compute_cost_readonly(self):
        user = self.env.user
        for rec in self:
            if user.has_group("sha_pro_cost_access.group_access_product_cost"):
                rec.cost_readonly = True
            else:
                rec.cost_readonly = False
