# -*- coding: utf-8 -*-

{
    'name': 'kushki Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Kushki',
    'version': '11.0.1',
    'author' : 'Libretec Juan Cristobal Lopez',
    "support": 'apps@libretec.coop',
    "website": 'https://libretec.coop',
    "license": "LGPL-3",
    'description': """Kushki Payment Acquirer
                  https://www.kushkipagos.com/""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_kushki_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
}
