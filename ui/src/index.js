const m = require("mithril")
const { PathView } = require("./archives")

m.route.prefix = ''
m.route(document.getElementById("main"), '/:path...', {
    '/:path...': PathView,
});
