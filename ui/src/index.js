const m = require("mithril")
const { DirectoryList } = require("./directory")

m.route(document.getElementById("main"), '/', {
    '/': DirectoryList,
    '/:path...': DirectoryList,
});
