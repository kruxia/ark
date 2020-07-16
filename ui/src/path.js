const m = require("mithril")

var Path = {
    data: {},
    path: '',
    load: function (path) {
        path = path || ''
        return m.request({
            method: 'GET',
            url: 'http://localhost:8000/ark/' + path,
            withCredentials: false,
        }).then(function (result) {
            Path.data = result
            Path.path = path
        })
    },
}

var PathLink = {
    view: function (vnode) {
        return (
            <span>{vnode.attrs.prefix || ''}
                <a href={vnode.attrs.path} onclick={(event) => {
                    // TODO: Back button not working
                    event.preventDefault()
                    m.route.set('/:path...', { path: vnode.attrs.path })
                    Path.load(vnode.attrs.path)
                }}>
                    {vnode.attrs.name}
                </a>
            </span>
        )
    }
}

var Breadcrumbs = {
    view: function () {
        return (
            <div class="mx-2">
                <PathLink path="" name="archives" />
                {
                    Path.path.split('/').map((slug, index) => {
                        if (slug) {
                            var path = Path.path.split('/').slice(0, index + 1).join('/')
                            return <PathLink path={path} name={slug} prefix=" > " />
                        }
                        else
                            return ""
                    })
                }
            </div>
        )
    }
}

var DirectoryView = {
    view: function () {
        return (
            <table class="table-auto w-full">
                <thead>
                    <tr>
                        <th class="border-b px-2 py-2 text-left">name</th>
                        <th class="border-b px-2 py-2 text-left">size</th>
                        <th class="border-b px-2 py-2 text-left">last modified</th>
                        <th class="border-b px-2 py-2 text-right">rev</th>
                    </tr>
                </thead>
                <tbody>
                    {Path.data.files.map((item, index) => {
                        var item_path = (
                            Path.path + '/' + item.path.name
                        ).replace(/^\//, '')
                        return (
                            <tr key={index}>
                                <td class="border-b px-2 py-2 text-left align-top">
                                    <a href={item_path} onclick={(event) => {
                                        // TODO: Back button not working
                                        event.preventDefault()
                                        m.route.set('/:path...', { path: item_path })
                                        Path.load(item_path)
                                    }}>
                                        {item.path.name}
                                    </a>
                                </td>
                                <td class="border-b px-2 py-2 text-left align-top">
                                    {
                                        // TODO: Readable size
                                        item.path.size
                                    }
                                </td>
                                <td class="border-b px-2 py-2 text-left align-top">
                                    {
                                        // TODO: Better date formatting
                                        item.version.date
                                            .replace(/\.\d+/, '').replace('T', ' ')
                                            .replace('+00:00', ' UTC')
                                    }
                                </td>
                                <td class="border-b px-2 py-2 text-right align-top">
                                    {
                                        item.version.rev
                                    }
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        )
    }
}

var FileView = {
    view: function () {
        return (
            // TODO: replace this with a more responsible method of creating a preview
            // (since this will only work for files that are already displayable.)
            <div class="m-2 border w-auto h-screen">
                <iframe src={Path.data.info.path.url} class="w-full h-full" />
            </div>
        )
    }
}

var PathView = {
    oninit: (vnode) => {
        Path.load(vnode.attrs.path)
    },
    view: function () {
        if (Path.data.files) {
            return <DirectoryView />
        } else if (Path.data.info && Path.data.info.path.kind == 'file') {
            return <FileView />
        } else {
            return "loading..."
        }
    }
}

var ArchiveView = {
    view: function () {
        return (
            <div>
                <Breadcrumbs />
                <PathView />
            </div>
        )
    }
}

module.exports = { ArchiveView }
