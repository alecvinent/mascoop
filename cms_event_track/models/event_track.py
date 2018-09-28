# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo import fields
from odoo import tools

testing = tools.config.get('test_enable')


if not testing:
    # prevent these forms to be registered when running tests

    class EventTrackForm(models.AbstractModel):
        """Propuesta para el evento."""

        _name = 'cms.form.event.track'
        _inherit = 'cms.form'
        _form_model = 'event.track'
        _form_model_fields = ('event_id',
                        'name',
                        'type_id',
                       'product_id',
                        'theme_tag',
                          'partner_id_name',
                          'partner_company_name',
                          'country_id',

                       # 'final_tag_id',
                        'resumen',
                        'is_moderator')
        _form_required_fields = ('event_id',
                                 'name',
                                 'type_id',
                                 'product_id',
                                 'theme_tag',
                                 'partner_id_name',
                                 'country_id',
                                 'resumen')
        _form_fields_order = _form_model_fields

        @property
        def form_title(self):
            return ('Una vez enviada su propuesta, favor de completar registro.')
        @property
        def form_msg_success_created(self):
            return ('Ponencia recibida. Una vez aprobada, recibirá indicaciones para  su inscripción.')

    class EventTrackSearchForm(models.AbstractModel):
        """EventTrack model search form."""

        _name = 'cms.form.search.event.track'
        _inherit = 'cms.form.search'
        _form_model = 'event.track'
        _form_model_fields = ('name', 'type_id','theme_tag', )
