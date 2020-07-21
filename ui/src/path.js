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
    query: new URLSearchParams(),
    load: function (path, queryStr) {
        path = path || PATH.path
        queryStr = queryStr || window.location.search
        var url = 'http://localhost:8000/ark/' + path + queryStr
        return m.request({
            method: 'GET',
            url: url,
            withCredentials: false,
        }).then(function (result) {
            PATH.data = result
            PATH.path = path
            PATH.query = new URLSearchParams(queryStr)
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
                            return <PathLink path={path} query={PATH.query} name={slug} prefix=" > " />
                        }
                        else {
                            return ""
                        }
                    })
                }
                &#x2002;
                {
                    PATH.query.has('rev') ? ('@ rev=' + PATH.query.get('rev')) : ''
                }
                &#x2002;
                {
                    PATH.query.has('rev') ? <PathLink path={'/' + PATH.path} name="view current"/> : ''
                }
            </span>
        )
    }
}

var PathLink = {
    view: function (vnode) {
        var href = vnode.attrs.path
        if (vnode.attrs.query && vnode.attrs.query.toString() != '') {
            href = href + '?' + vnode.attrs.query.toString()
        }
        return (
            <span>{vnode.attrs.prefix || ''}
                <a href={href} onclick={(event) => { PathLink.clickLink(event, vnode) }}>
                    {decodeURI(vnode.attrs.name)}
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