from odoo import models, fields

class AccountEdiXmlUBL21Zatca(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_21.zatca"

    def _l10n_sa_get_line_prepayment_vals(self, line, taxes_vals):
        if not line.move_id._is_downpayment() and line.sale_line_ids and all(sale_line.is_downpayment for sale_line in line.sale_line_ids):
            prepayment_move_id = line.sale_line_ids.invoice_lines.move_id.filtered(lambda m: m.move_type == 'out_invoice' and m._is_downpayment())
            if len(prepayment_move_id) > 1:
                prepayment_ids = ', '.join(prepayment_move_id.mapped('name'))
                issue_date = min(prepayment_move_id.mapped('l10n_sa_confirmation_datetime'))
                return {
                    'prepayment_id': prepayment_ids,
                    'issue_date': fields.Datetime.context_timestamp(
                        self.with_context(tz='Asia/Riyadh'),
                        issue_date,
                    ),
                    'document_type_code': 386,
                }
            else:
                return super()._l10n_sa_get_line_prepayment_vals(line, taxes_vals)
        return {}