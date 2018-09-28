/* Copyright 2017 OCA/oscar@vauxoo.com
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define("cms_event_track.tour", function (require) {
    "use strict";

    var Tour = require("web.Tour");
    var core = require('web.core');
    var _t = core._t;

    Tour.register({
        id: "website_create_track",
        name: "Create a track for the event",
        path: "/eventtrack/add",
        // mode: "test",
        steps: [
            {
                title: "Complete los datos de su propuesta (Ponencia, Poster o Panel)",
                element: "button.btn-primary:contains(Submit)",
                onload: function () {
                    $('input[name="name"]').val('Nueva Propuesta');
                    });
                }
            },
            {
                title: _t("Propuesta creada"),
                waitFor: "alert alert-info alert-dismissible:contains(Propuesta creada)",
                content:   _t("Esta es su propuesta. Puede modificarla."),
                popover:   { next: _t("Continuar") }
            }
        ]
    });

});
