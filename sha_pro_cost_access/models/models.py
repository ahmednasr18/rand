# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price',
        # groups="",
        groups="!sha_pro_cost_access.group_access_product_cost",
        help="""Value of the product (automatically computed in AVCO).
            Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
            Used to compute margins on sale orders.""")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(
        'Cost', company_dependent=True,
        digits='Product Price',
        # groups="",
        groups="!sha_pro_cost_access.group_access_product_cost",
        help="""Value of the product (automatically computed in AVCO).
            Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
            Used to compute margins on sale orders.""")
