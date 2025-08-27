# -*- coding: utf-8 -*-
# Copyright 2022 IZI PT Solusi Usaha Mudah
from odoo import models, fields
from odoo.exceptions import UserError
import io
import pathlib
from io import StringIO, BytesIO
import pandas
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

file_code = '''
attachment = env['ir.attachment'].browse(%s)
if not attachment:
    izi.alert('Attachment Not Found')
try:
    kwargs = {
        'nrows': %s,
    }
    res_dataframe = izi.read_attachment_df(attachment, **kwargs)
    izi_table.get_table_fields_from_dataframe(res_dataframe)
except Exception as e:
    izi.alert(str(e))
'''

auth_google_sheet_code = '''
pandas = izi.lib('pandas')
try:
    spreadsheet = izi.get_authorized_gsheet('{google_sheet_id}', '{google_sheet_json_key_attachment_name}')
    worksheet_titles = [worksheet.title for worksheet in spreadsheet.worksheets()]
    if '{google_sheet_name}' not in worksheet_titles:
        izi.alert('Sheet Not Found')
    worksheet = spreadsheet.worksheet('{google_sheet_name}')
    data_with_header = worksheet.get_all_values()
    header = data_with_header[0]
    if {limit} >= 1:
        data = data_with_header[1:{limit}]
    else:
        data = data_with_header[1:]
    res_dataframe = pandas.DataFrame(data, columns=header)
    izi_table.get_table_fields_from_dataframe(res_dataframe)
except Exception as e:
    izi.alert(str(e))
'''
public_google_sheet_code = '''
pandas = izi.lib('pandas')
try:
    gsheet_url = "https://docs.google.com/spreadsheets/d/{google_sheet_id}/gviz/tq?tqx=out:csv&sheet={google_sheet_name}"
    res_dataframe = pandas.read_csv(gsheet_url, nrows={limit})
    izi_table.get_table_fields_from_dataframe(res_dataframe)
except Exception as e:
    izi.alert(str(e))
'''


class IZIDataSourceItem(models.Model):
    _inherit = 'izi.data.source.item'

    type = fields.Selection(
        selection_add=[
            ('file', 'File CSV / XLS'),
            ('google_sheet', 'Google Sheet'),
        ], ondelete={'file': 'cascade', 'google_sheet':'cascade'})
    file_attachment_id = fields.Many2one('ir.attachment', string='File', domain=[('mimetype', 'in',
        ('application/vnd.ms-excel', 
        'text/csv', 
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))])
    google_sheet_id = fields.Char('Sheet ID', required=False)
    google_sheet_name = fields.Char('Sheet Name', required=False)
    google_sheet_json_key_attachment_id = fields.Many2one('ir.attachment', string='JSON Key File', required=False, domain=[('mimetype', '=',
        'application/json')])

    def process_data(self):
        if not self.table_id:
            table = self.env['izi.table'].create({
                'name': self.name,
                'is_stored': True,
                'is_direct': True,
                'source_id': self.source_id.id,
            })
            self.table_id = table.id
        
        if self.table_id and self.table_id.cron_id and self.table_id.is_direct:
            if self.type == 'file':
                if self.file_attachment_id:
                    self.table_id.cron_id.code = file_code % (self.file_attachment_id.id, self.limit)
                    self.table_id.method_direct_trigger()
                else:
                    raise UserError('File Not Found')
            elif self.type == 'google_sheet':
                if self.google_sheet_id and self.google_sheet_name:
                    if self.google_sheet_json_key_attachment_id:
                        self.table_id.cron_id.code = auth_google_sheet_code.format(**{
                            'google_sheet_id': self.google_sheet_id,
                            'google_sheet_name': self.google_sheet_name.replace(' ', '%20'),
                            'google_sheet_json_key_attachment_name': self.google_sheet_json_key_attachment_id.name,
                            'limit': self.limit,
                        })
                    else:
                        self.table_id.cron_id.code = public_google_sheet_code.format(**{
                            'google_sheet_id': self.google_sheet_id,
                            'google_sheet_name': self.google_sheet_name.replace(' ', '%20'),
                            'limit': self.limit,
                        })
                    self.table_id.method_direct_trigger()
                else:
                    raise UserError('Google Sheet URL and Sheet Name Must Be Filled!')
        else:
            raise UserError('The Table Must Use Direct Script!')
        return True