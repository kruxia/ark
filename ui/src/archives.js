const m = require("mithril")
const { fileSizeStr } = require('./lib')
const { IconArchiveNew, IconFolderNew, IconUpload, IconCopy, IconDelete, IconHistory, IconHistoryOff } = require('./icons')
const { HistoryPanel } = require('./history-panel')
var { PATH, Breadcrumbs, PathLink } = require('./path')
var ARCHIVE_URL = process.env.ARCHIVE_URL

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
        } else {
            // nothing yet
            // return <div class="mx-2">loading...</div>
        }
    }
}

var ArchivesView = {
    view: function () {
        return (
            <div>
                <Breadcrumbs />
                <ArchivesActions />
                <DirectoryList />
            </div>
        )
    }
}

var ArchivesActions = {
    view: function () {
        return (
            <div class="mx-2">
                <ActionCreateArchive />
            </div>
        )
    }
}

var DirectoryView = {
    view: function () {
        return (
            <div>
                <Breadcrumbs />
                <DirectoryActions />
                <div class="flex flex-wrap flex-row-reverse justify-end -mx-2">
                    <div class="ml-2 mr-4 w-full md:w-5/12 lg:w-4/12">
                        <HistoryPanel />
                    </div>
                    <div class="ml-4 mr-2 w-full md:w-6/12 lg:w-7/12">
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
            <div class="mx-2">
                <ActionCreateFolder />
                <ActionUploadFile />
                <ActionViewHistory />
                <ActionCopyArchiveURL />
            </div>
        )
    }
}

var DirectoryList = {
    view: function () {
        return (
            <div class="p-2 border shadow">
                <h2>Contents</h2>
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
                        {
                            PATH.data.files.map((item, index) => {
                                var item_path = ('/' + PATH.path + '/' + item.path.name).replace(/^\/\//, '/')
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
                            })
                        }
                    </tbody>
                </table>
            </div>
        )
    }
}

var FileView = {
    view: function () {
        return (
            <div>
                <Breadcrumbs />
                <FileActions />
                <div>
                    <div class="mx-2 w-full">
                        <HistoryPanel />
                    </div>
                    <div class="mx-2 w-full">
                        <FileIFrame />
                    </div>
                </div>
            </div>
        )
    }
}

var FileActions = {
    view: function () {
        return (
            <div class="mx-2">
                <ActionViewHistory />
            </div>
        )
    }
}

var FileIFrame = {
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

// Create an Archive
var ActionCreateArchive = {
    view: function () {
        return (
            <span class="mr-2">
                <a href="" onclick={ActionCreateArchive.create}>
                    <IconArchiveNew class="h-6 mr-1" />
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
            <a href="" onclick={ActionCreateFolder.create}>
                <span class="mr-2">
                    <IconFolderNew class="h-6 mr-1 align-top" />
                    Create Folder
                </span>
            </a>
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
                <IconUpload class="h6 mr-1 align-top" />
                <a href="" onclick={ActionUploadFile.click}>Upload File</a>
                <form class="inline" enctype="multipart/form-data" class="hidden">
                    <input id="upload_file" name="file" type="file" onchange={ActionUploadFile.upload} />
                </form>
            </span>
        )
    },
    click: function (event) {
        event.preventDefault();
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
            }).catch((error) => {
                console.log(error.response)
                alert(error.response.error)
            })
        }
    }
}

var ActionCopyArchiveURL = {
    view: function () {
        return (
            <span class="mr-2">
                <a href="" onclick={ActionCopyArchiveURL.click}>
                    <IconCopy class="h-6 mr-1" />
                    Copy URL
                </a>
                <input type="text" id="path-archive-url-data" value={'http://localhost:7000/' + PATH.path} class="w-full opacity-0 absolute" hidden="hidden" />
            </span>
        )
    },
    click: function (event) {
        event.preventDefault()
        var element = document.getElementById('path-archive-url-data')
        element.hidden = false
        element.select()
        element.setSelectionRange(0, 99999)
        document.execCommand('copy')
        element.hidden = true
        alert('Copied URL: ' + element.value)
    }
}

// == PATH ACTIONS ==
// (both files and directories)

var ActionViewHistory = {
    view: function () {
        if (HistoryPanel.visible == false) {
            return (
                <a href="" class="mr-2" onclick={ActionViewHistory.viewHistory}>
                    <IconHistory class="h6 mr-1 align-top" />
                    View History
                </a>
            )
        } else {
            return (
                <a href="" class="mr-2" onclick={ActionViewHistory.viewHistory}>
                    <IconHistoryOff class="h6 mr-1 align-top" />
                    Hide History
                </a>
            )
        }
    },
    viewHistory: function (event) {
        event.preventDefault()
        if (HistoryPanel.visible == false) {
            HistoryPanel.load()
            HistoryPanel.visible = true
        } else {
            HistoryPanel.visible = false
        }
    }
}

var ActionDeletePath = {
    view: function () {
        return (
            <span class="mr-2">
                <IconDelete class="h6 mr-1 align-top" />
                Delete
            </span>
        )
    }
}

module.exports = { ArchivePathView }
