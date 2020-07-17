const m = require("mithril")
const { ArchiveView } = require("./path")

m.route.prefix = ''
m.route(document.getElementById("main"), '/', {
    '/': ArchiveView,
    '/:path...': ArchiveView,
});
