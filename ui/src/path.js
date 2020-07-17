const m = require("mithril")

var PATH = {
    data: {},
    path: '',
    load: function (path) {
        path = path || ''
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

var PathLink = {
    view: function (vnode) {
        return (
            <span>{vnode.attrs.prefix || ''}
                <a href={vnode.attrs.path} onclick={(event) => {
                    // TODO: Back button not working
                    event.preventDefault()
                    m.route.set('/:path...', { path: vnode.attrs.path })
                    PATH.load(vnode.attrs.path)
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
                    PATH.path.split('/').map((slug, index) => {
                        if (slug) {
                            var path = PATH.path.split('/').slice(0, index + 1).join('/')
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
                        <th class="border-b px-2 py-2 text-left w-24">size</th>
                        <th class="border-b px-2 py-2 text-left w-56">last modified</th>
                        <th class="border-b px-2 py-2 text-right w-8">rev</th>
                    </tr>
                </thead>
                <tbody>
                    {PATH.data.files.map((item, index) => {
                        var item_path = (
                            PATH.path + '/' + item.path.name
                        ).replace(/^\//, '')
                        return (
                            <tr key={index}>
                                <td class="border-b px-2 py-2 text-left align-top">
                                    <a href={item_path} onclick={(event) => {
                                        // TODO: Back button not working
                                        event.preventDefault()
                                        m.route.set('/:path...', { path: item_path })
                                        PATH.load(item_path)
                                    }}>
                                        {item.path.name}
                                    </a>
                                </td>
                                <td class="border-b px-2 py-2 text-left align-top">
                                    {
                                        // TODO: Readable size
                                        fileSizeStr(item.path.size)
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
                <iframe src={PATH.data.info.path.url} class="w-full h-full" />
            </div>
        )
    }
}

var PathView = {
    oninit: (vnode) => {
        PATH.load(vnode.attrs.path)
    },
    view: function () {
        if (PATH.data.files) {
            return <DirectoryView />
        } else if (PATH.data.info && PATH.data.info.path.kind == 'file') {
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

// Given a file size in bytes, return a size string
const FILE_SIZE_K = 1000
const FILE_SIZE_SUFFIX = 'B'
const FILE_SIZE_DECIMALS = 1
const FILE_SIZE_SEP = '\u00a0'
const FILE_SIZE_UNITS = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
const FILE_SIZE_UNITS_LAST_INDEX = FILE_SIZE_UNITS.length - 1

function fileSizeStr(size) {
    if (!size) {
        return ''
    }
    for (unit of FILE_SIZE_UNITS) {
        if (
            Math.abs(size) < FILE_SIZE_K
            || unit == FILE_SIZE_UNITS[FILE_SIZE_UNITS_LAST_INDEX]
        ) {
            return (
                (unit == '' ? size : size.toFixed(FILE_SIZE_DECIMALS))
                + FILE_SIZE_SEP
                + unit
                + (unit == '' ? 'bytes' : FILE_SIZE_SUFFIX)
            )
        }
        size = size / FILE_SIZE_K
    }
}

module.exports = { ArchiveView }
