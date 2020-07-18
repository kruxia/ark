const m = require("mithril")
const { ArchivePathView } = require("./archives")

m.route.prefix = ''
m.route(document.getElementById("main"), '/:path...', {
    '/:path...': ArchivePathView,
});
