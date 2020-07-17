const m = require("mithril")
const { fileSizeStr } = require('./lib')

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

var PathView = {
    oninit: (vnode) => {
        PATH.load(vnode.attrs.path)
    },
    view: function () {
        if (!PATH.data.info && PATH.data.files) {
            // List Archives View
            return (
                <div>
                    <Breadcrumbs />
                    <div class="mx-2">
                        <CreateArchive />
                    </div>
                    <DirectoryView />
                </div>
            )
        } else if (PATH.data.files) {
            // DirectoryView
            return (
                <div>
                    <Breadcrumbs />
                    <div class="mx-2">
                        <CreateFolder />
                    </div>
                    <DirectoryView />
                </div>
            )
        } else if (PATH.data.info && PATH.data.info.path.kind == 'file') {
            // File View
            return (
                <div>
                    <Breadcrumbs />
                    <FileView />
                </div>
            )
        } else {
            // nothing yet
            return <div class="mx-2">loading...</div>
        }
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
                                    <PathLink path={item_path} name={item.path.name} />
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
        // m.route.set('/:path...', { path: vnode.attrs.path })
        // PATH.load(vnode.attrs.path)
    }

}

var Breadcrumbs = {
    view: function () {
        return (
            <div class="mx-2">
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
            </div>
        )
    }
}

// Create an Archive
var CreateArchive = {
    view: function () {
        return (
            <span class="mr-2">
                <a href="" onclick={CreateArchive.viewModal}>Create Archive</a>
            </span>
        )
    },
    viewModal: function (event) {
        event.preventDefault();
        const archiveName = window.prompt("Archive Name:", "")
        if (archiveName) {
            m.request({
                // POST the request to create a new archive
                method: 'POST',
                url: 'http://localhost:8000/ark',
                withCredentials: false,
                body: { name: archiveName },
            }).then(function (response) {
                PATH.load('')
            }).catch(function (error) {
                if (error.response) {
                    alert(error.response.message)
                }
            })
        }
    }
}

// == PATH ACTIONS ==
// (both files and directories)

var ViewHistory = {
    view: function () {
        return (
            <span class="mr-2 text-gray-500">
                View History
            </span>
        )
    }
}

// == DIRECTORY ACTIONS ==
// (only on directories)

var CreateFolder = {
    view: function () {
        return (
            <span class="mr-2 text-gray-500">
                Create Folder
            </span>
        )
    }
}

var UploadFile = {
    view: function () {
        return (
            <span class="mr-2 text-gray-500">
                Upload File
            </span>
        )
    }
}


module.exports = { PathView }
