const m = require('mithril')

var ACTIONS = {
    A: 'Added',
    D: 'Deleted',
    M: 'Modified',
    R: 'Replaced',
}

var PATH = {
    data: {},
    path: '',
    load: function (path) {
        path = path || PATH.path
        return m.request({
            method: 'GET',
            url: 'http://localhost:8000/ark/' + path,
            withCredentials: false,
        }).then(function (result) {
            PATH.data = result
            PATH.path = path
        })
    },
}

var Breadcrumbs = {
    view: function () {
        return (
            <span class="mx-2">
                <PathLink path="/" name="archives" />
                {
                    PATH.path.split('/').map((slug, index) => {
                        if (slug) {
                            var path = "/" + PATH.path.split('/').slice(0, index + 1).join('/')
                            return <PathLink path={path} name={slug} prefix=" > " />
                        }
                        else {
                            return ""
                        }
                    })
                }
            </span>
        )
    }
}

var PathLink = {
    view: function (vnode) {
        return (
            <span>{vnode.attrs.prefix || ''}
                <a href={vnode.attrs.path} onclick={(event) => { PathLink.clickLink(event, vnode) }}>
                    {vnode.attrs.name}
                </a>
            </span>
        )
    },
    clickLink: function (event, vnode) {
        // TODO: Back button not working
        // event.preventDefault()
        // m.route.set('/:path...', { 'path': vnode.attrs.path || '' })
        // PATH.load(vnode.attrs.path)
    }

}

module.exports = { ACTIONS, PATH, Breadcrumbs, PathLink }