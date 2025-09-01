{
    'name' : 'Base Stages',
    'version' : '1.2',
    'summary': 'Base Stages',
    'sequence': 10,
    'description': """
    """,
    'category': 'Extra Tools',
    'version': '17.0.0.1',
    'author': 'LOXEL-TEXHNOLOGY',
    'website': 'loxeltechnology.com',
    'depends' : ['base',
                 'mail',
                 'web'],
    'data': [
        "security/ir.model.access.csv",
        "views/res_stage.xml",
        "views/menu_items.xml"
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}