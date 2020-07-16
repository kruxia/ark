const m = require("mithril")
const { PathView } = require("./path")

m.route(document.getElementById("main"), '/', {
    '/': PathView,
    '/:path...': PathView,
});
