# -*- coding: utf-8 -*-
{
    'name': "hr_mascoop",

    'summary': """
        hr Personalizacion Mascoop""",

    'description': """
        Modificaciones a hr
    """,

    'author': "Juan Cristobal Lopez",
    'website': "https://libretec.coop",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '11.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
