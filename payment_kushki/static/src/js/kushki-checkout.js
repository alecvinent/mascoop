var KushkiCheckout, bind = function(t, e) {
    return function() {
        return t.apply(e, arguments)
    }
};
KushkiCheckout = function() {
    function t(t, e) {
        this.params = t,
        this.onReceiveMessage = bind(this.onReceiveMessage, this),
        this.params.is_subscription = this.params.is_subscription || !1,
        this.params.language = this.params.language || "es",
        this.params.currency = this.params.currency || "USD",
        this.params.payment_methods = this.params.payment_methods || ["credit-card"],
        this.params.callback_url = this.params.callback_url || null,
        this.params.redirect_mode = this.params.redirect_mode || null,
        this.url = e || "https://cdn.kushkipagos.com/index.html",
        this.id = +new Date,
        this.iframeHeightOffset = 10,
        this.form = document.getElementById(this.params.form),
        this.iframe = document.createElement("iframe"),
        this._loadIframe(),
        this._listenForMessages()
    }
    return t.prototype.onReceiveMessage = function(t) {
        if (t.origin === this.expectedOrigin()) return this.processMessage(t.data)
    }, t.prototype.expectedOrigin = function() {
        var t;
        return t = this.url.split("/"), t[0] + "//" + t[2]
    }, t.prototype.processMessage = function(t) {
        var e, s, i;
        switch (i = t.split(":"), s = i[0], e = i[1], s) {
            case "height":
                return this._adjustHeight(e);
            case "parameters":
                return this._setParameters(e)
        }
    }, t.prototype._loadIframe = function() {
        var t, e, s, i;
        s = this.url + "?merchant_id=" + this.params.merchant_id +
        ("&is_subscription=" + this.params.is_subscription) +
        ("&amount=" + encodeURIComponent(JSON.stringify(this.params.amount))) +
        ("&language=" + this.params.language) +
        ("&currency=" + this.params.currency) +
        ("&payment_methods=" + this.params.payment_methods) +
        ("&callback_url=" + this.params.callback_url) +
        ("&redirect_mode=" + this.params.redirect_mode), t = {
            src: s,
            width: "100%",
            style: "display:block",
            name: "kushki-iframe",
            id: this.id,
            scrolling: "no",
            frameborder: "0"
        };
        for (e in t) i = t[e], this.iframe.setAttribute(e, i);
        return this.form.appendChild(this.iframe)
    }, t.prototype._listenForMessages = function() {
        return window.addEventListener("message", this.onReceiveMessage, !1)
    }, t.prototype._createInput = function(t, e) {
        var s, i, r, a;
        i = document.createElement("input"), s = {
            type: "hidden",
            name: e,
            value: t.trim()
        };
        for (r in s) a = s[r], i.setAttribute(r, a);
        return i
    }, t.prototype._adjustHeight = function(t) {
        return this.iframe.height = this.iframeHeightOffset + parseInt(t, 10)
    }, t.prototype._setParameters = function(t) {
        var e, s, i, r, a;
        return r = t.split(","),
        a = r[0], e = r[1],
        i = this._createInput(a, "kushkiToken"),
        s = this._createInput(e, "kushkiDeferred"),
        this.form.appendChild(i),
        this.form.appendChild(s),
        this.form.submit()
    }, t
}();