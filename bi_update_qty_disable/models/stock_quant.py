# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, _
from odoo.exceptions import ValidationError

class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    def change_product_qty(self):
        res = super(StockChangeProductQty, self).change_product_qty()
        if not self.env.user.has_group("bi_update_qty_disable.group_onhand_qty_user"):
            raise ValidationError(
                _("You don't have access rights for update on hand quantity!"))
        return res
