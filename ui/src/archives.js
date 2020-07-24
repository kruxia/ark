const m = require("mithril")
const { fileSizeStr } = require('./lib')
const {
    IconArchiveNew, IconFolderNew, IconUpload, IconDownload, IconCopy, IconDelete,
    IconHistory, IconHistoryOff, IconSpinningCircles
} = require('./icons')
const { HistoryPanel } = require('./history')
const { PATH, Breadcrumbs, PathLink } = require('./path')
const { ErrorView } = require('./error')

var ArchivePathView = {
    oninit: (vnode) => {
        PATH.load(vnode.attrs.path)
    },
    view: function () {
        if (!PATH.data.info && PATH.data.files) {
            // List Archives View
            return <ArchivesView />
        } else if (PATH.data.files) {
            return <DirectoryView />
        } else if (PATH.data.info && PATH.data.info.path.kind == 'file') {
            // File View
            return <FileView />
        } else if (PATH.error) {
            return <ErrorView />
        } else {
            // nothing yet
            // return <div class="mx-2">loading...</div>
        }
    }
}

var ArchivesView = {
    view: function () {
        return (
            <div class="leading-tight">
                <div class="text-2xl font-light">
                    <Breadcrumbs />
                </div>
                <div class="flex flex-wrap flex-row-reverse justify-end">
                    <div class="w-full sm:w-5/12 sm:px-4">
                        <ArchivesActions />
                    </div>
                    <div class="w-full pr-2 sm:w-7/12">
                        <DirectoryList />
                    </div>
                </div>
            </div>
        )
    }
}

var ArchivesActions = {
    view: function () {
        return (
            <ul class="mx-2 leading-relaxed">
                <li class="my-2"><ActionCreateArchive /></li>
            </ul>
        )
    }
}

var DirectoryView = {
    view: function () {
        return (
            <div class="leading-tight">
                <div class="text-2xl font-light">
                    <Breadcrumbs />
                </div>
                <div class="flex flex-wrap flex-row-reverse justify-end">
                    <div class="w-full sm:w-5/12 sm:px-4">
                        <DirectoryActions />
                        <HistoryPanel />
                    </div>
                    <div class="w-full pr-2 sm:w-7/12">
                        <DirectoryList />
                    </div>
                </div>
            </div>
        )
    }
}

var DirectoryActions = {
    view: function () {
        return (
            <ul class="leading-relaxed mx-2">
                <li class="my-2"><ActionCopyArchiveURL /></li>
                <li class="my-2"><ActionCreateFolder /></li>
                <li class="my-2"><ActionUploadFile /></li>
                <li class="my-2"><ActionDownloadThisPath /></li>
                <li class="my-2"><ActionDeleteThisPath /></li>
                <li class="my-2"><ActionViewHistory /></li>
            </ul>
        )
    }
}

var DirectoryList = {
    view: function () {
        return (
            <div class="px-2 mt-2">
                <table class="table-auto w-full">
                    <thead>
                        <tr>
                            <th class="align-bottom border-b leading-none py-2 pr-2 text-left w-64 md:w-auto">
                                name
                            </th>
                            <th class="align-bottom border-b leading-none py-2 pr-2 text-left">
                                size
                            </th>
                            <th class="align-bottom border-b leading-none py-2 pr-2 text-left">
                                last modified
                            </th>
                            <th class="align-bottom border-b leading-none py-2 text-right w-8">
                                rev
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            PATH.data.files.map((item, index) => {
                                return <DirectoryListItem item={item} index={index} />
                            })
                        }
                    </tbody>
                </table>
            </div>
        )
    }
}

var DirectoryListItem = {
    view: function (vnode) {
        var item = vnode.attrs.item
        var index = vnode.attrs.index
        var item_path = ('/' + PATH.path + '/' + item.path.name).replace(/^\/\//, '/')
        return (
            <tr key={index}>
                <td class="border-b pr-2 py-2 text-left align-top">
                    <PathLink path={item_path} name={item.path.name} query={PATH.query} />
                </td>
                <td class="border-b pr-2 py-2 text-left align-top">
                    {
                        // TODO: Readable size
                        fileSizeStr(item.path.size)
                    }
                </td>
                <td class="border-b pr-2 py-2 text-left align-top">
                    {
                        // TODO: Better date formatting
                        item.version.date
                            .replace(/\.\d+/, '').replace('T', ' ')
                            .replace('+00:00', ' UTC')
                    }
                </td>
                <td class="border-b py-2 text-right align-top">
                    {
                        item.version.rev
                    }
                </td>
            </tr>
        )
    }
}

var FileView = {
    view: function () {
        return (
            <div class="h-screen leading-relaxed">
                <div class="text-2xl font-light">
                    <Breadcrumbs />
                </div>
                <div class="h-full flex flex-wrap flex-row-reverse justify-end">
                    <div class="w-full sm:w-5/12">
                        <FileActions />
                        <HistoryPanel />
                    </div>
                    <div class="h-full w-full sm:w-7/12">
                        {
                            PATH.mimetype.match(/(?:^(?:text|image)|(?:xml|pdf)$)/) ? (
                                <FileIFrame />
                            ) : (
                                    <FileNoPreview />
                                )
                        }
                    </div>
                </div>
            </div>
        )
    }
}

var FileActions = {
    view: function () {
        return (
            <ul class="leading-relaxed mx-2">
                <li class="my-2"><ActionDownloadThisPath /></li>
                <li class="my-2"><ActionDeleteThisPath /></li>
                <li class="my-2"><ActionViewHistory /></li>
            </ul>
        )
    }
}

var FileIFrame = {
    view: function () {
        return (
            // TODO: replace this with a more responsible method of creating a preview
            // (since this will only work for files that are already displayable.)
            <div class="m-2 w-auto h-full">
                <iframe src={PATH.data.info.path.url} class="w-full h-full" />
            </div>
        )
    }
}

var FileNoPreview = {
    view: function () {
        return (
            <div class="m-2 w-auto h-full">
                <h2 class="text-lg font-black">Preview Unavailable</h2>
                <p class="mb-2">
                    No preview is available for <span class="font-semibold">{PATH.path.match(/\.[^\.]*$/)}</span> files.
                    You can use the "Export" action to download and preview the file
                    on your system.
                </p>
            </div>
        )
    }
}

// Create an Archive
var ActionCreateArchive = {
    view: function () {
        return (
            <span class="mr-2">
                <a href="" onclick={ActionCreateArchive.create}>
                    <IconArchiveNew class="w-6 mr-1" />
                    Create Archive
                </a>
            </span>
        )
    },
    create: function (event) {
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
                // browse to the new archive
                window.location = '/' + archiveName
            }).catch(function (error) {
                if (error.response) {
                    alert(error.response.message)
                }
            })
        }
    }
}

// == DIRECTORY ACTIONS ==
// (only on directories)

var ActionCreateFolder = {
    view: function () {
        return (
            <button onclick={this.create}>
                <span class="mr-2">
                    <IconFolderNew class="w-6 mr-1 align-top" />
                    Create Subfolder
                </span>
            </button>
        )
    },
    create: function (event) {
        event.preventDefault();
        const folderName = window.prompt("Folder Name:", "")
        console.log(folderName)
        if (folderName) {
            const url = 'http://localhost:8000/ark/' + PATH.path + '/' + folderName
            console.log('PUT: ' + url)
            m.request({
                // PUT the request to create a new folder
                method: 'PUT',
                url: 'http://localhost:8000/ark/' + PATH.path + '/' + folderName,
                withCredentials: false,
            }).then(function (response) {
                // browse to the new folder
                window.location = '/' + PATH.path + '/' + folderName
            }).catch(function (error) {
                if (error.response) {
                    console.log(error.response)
                    alert(error.response.error)
                }
            })
        }
    }
}

var ActionUploadFile = {
    view: function () {
        return (
            <span class="mr-2">
                <IconUpload class="w-6 mr-1 align-top" />
                <button onclick={this.click}>Upload File</button>
                <form class="inline" enctype="multipart/form-data" class="hidden">
                    <input id="upload_file" name="file" type="file" onchange={ActionUploadFile.upload} />
                </form>
            </span>
        )
    },
    click: function (event) {
        document.getElementById('upload_file').click()
    },
    upload: function (event) {
        event.preventDefault()
        var form = event.target.parentNode
        // TODO: Support multiple file upload
        for (file of event.target.files) {
            const url = 'http://localhost:8000/ark/' + PATH.path + '/' + file.name
            var body = new FormData(form)
            body["file"] = file
            m.request({
                method: "PUT",
                url: url,
                body: body,
            }).then((result) => {
                console.log(result)
                PATH.load()
                HistoryPanel.load()
            }).catch((error) => {
                console.log(error.response)
                alert(error.response.error)
            })
        }
    }
}

var ActionDownloadThisPath = {
    view: function () {
        return (
            <span class="mr-2">
                <IconDownload class="w-6 mr-1 align-top" />
                <button onclick={this.click}>
                    Export {decodeURI(PATH.data.info.path.name)}
                    {PATH.query.has('rev') ? ' @ rev=' + PATH.query.get('rev') : ''}
                    {PATH.data.info.path.kind == 'dir' ? ' (.zip)' : ''}
                </button>
            </span>
        )
    },
    click: function () {
        var url = (
            'http://localhost:8000/export/' + PATH.path
            + (PATH.query.has('rev') ? '?rev=' + PATH.query.get('rev') : '')
        )
        window.open(url)
    }
}

var ActionCopyArchiveURL = {
    view: function () {
        const copyURL = 'http://localhost:7000/' + PATH.path
        return (
            <span class="mr-2">
                <button onclick={this.click}>
                    <IconCopy class="w-6 mr-1 align-text-top" />
                    Copy Archive URL
                </button>
                <input type="text" id="path-archive-url-data" value={copyURL} class="w-full opacity-0 absolute" hidden="hidden" />
            </span>
        )
    },
    click: function (event) {
        var element = document.getElementById('path-archive-url-data')
        element.hidden = false
        element.select()
        element.setSelectionRange(0, 99999)
        document.execCommand('copy')
        element.hidden = true
        alert('Copied Archive URL: ' + element.value)
    }
}

var ActionDeleteThisPath = {
    view: function () {
        if (PATH.path != PATH.data.info.archive.name && !PATH.query.has('rev')) {
            return (
                <a href={'/' + PATH.path} class="mr-2" onclick={this.delete}>
                    <IconDelete class="w-6 mr-1 align-top" />
                    Delete {decodeURI(PATH.data.info.path.name)}
                </a>
            )
        }
    },
    delete: function (event) {
        event.preventDefault()
        var deleteURL = event.target.getAttribute('href')
        console.log(PATH.data)
        if (confirm(
            'Delete ' + deleteURL + '?\nThe content will continue to be available in '
            + 'the history at ' + deleteURL + '?rev=' + PATH.data.info.version.rev
        )) {
            m.request({
                // DELETE the given path
                method: 'DELETE',
                url: 'http://localhost:8000/ark' + deleteURL,
                withCredentials: false,
            }).then(function (response) {
                // browse to the new archive
                var newLocation = deleteURL.replace(/\/[^\/]*$/, '')
                window.location = newLocation
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

var ActionViewHistory = {
    view: function () {
        if (HistoryPanel.waiting == true) {
            return (
                <div class="mr-2">
                    <IconSpinningCircles class="w-6 mr-1 align-top" />
                    Loading History...
                </div>
            )
        } else if (HistoryPanel.visible == false) {
            return (
                <button class="mr-2" onclick={this.viewHistory}>
                    <IconHistory class="w-6 mr-1 align-top" />
                    View History
                </button>
            )
        } else {
            return (
                <button class="mr-2" onclick={this.viewHistory}>
                    <IconHistoryOff class="w-6 mr-1 align-top" />
                    Hide History
                </button>
            )
        }
    },
    viewHistory: function (event) {
        event.preventDefault()
        if (HistoryPanel.visible == false) {
            HistoryPanel.load()
        } else {
            HistoryPanel.visible = false
        }
    }
}

var ActionDeletePath = {
    view: function () {
        return (
            <span class="mr-2">
                <IconDelete class="w-6 mr-1 align-top" />
                Delete
            </span>
        )
    }
}

module.exports = { ArchivePathView }
