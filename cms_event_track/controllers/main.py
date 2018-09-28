# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.cms_form.controllers.main import SearchFormControllerMixin
from odoo.addons.cms_form.controllers.main import FormControllerMixin


class EventtrackForm(http.Controller, FormControllerMixin):
    """Eventtrack form controller."""

    @http.route([
        '/eventtrack/add',
        '/eventtrack/<model("event.track"):main_object>/edit',
    ], type='http', auth='user', website=True)
    def cms_form(self, main_object=None, **kw):
        """Handle a `form` route.
        """
        model = 'event.track'
        return self.make_response(
            model, model_id=main_object and main_object.id, **kw)





class EventtrackListing(http.Controller, SearchFormControllerMixin):
    """Event Track search form controller."""

    @http.route([
        '/eventtrack',
        '/eventtrack/page/<int:page>',
    ], type='http', auth="public", website=True)
    def market(self, **kw):
        model = 'event.track'
        return self.make_response(model, **kw)
