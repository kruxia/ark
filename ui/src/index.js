const m = require("mithril")
const { ArchiveListView, ArchivePathView } = require("./archives")

m.route.prefix = ''
m.route(document.getElementById("main"), '/', {
    '/': ArchiveListView,
    '/:path...': ArchivePathView,
});
