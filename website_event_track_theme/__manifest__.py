# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advanced Events with Themes',
    'category': 'Marketing',
    'summary': 'Theme for tags and security group',
    'website': 'https://www.libretec.coop/page/events_libretec',
    'version': '1.0',
    'description': "",
    'depends': ['website_event_track'],
    'data': [
        'views/event_track_theme_views.xml',
        'views/event_track_portal.xml',
        'views/event.xml',
        'security/ir.model.access.csv'
        ],
}
