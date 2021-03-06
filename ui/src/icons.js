const m = require("mithril")

const IconArchive = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/archive-24px.svg"
      aria-label="icon: archive" alt="archive" title="archive" />
  )
}

const IconArchiveNew = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/archive-new-24px.svg"
      aria-label="icon: create new archive" alt="create new archive"
      title="create new archive" />
  )
}

const IconUpload = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/cloud_upload-24px.svg"
      aria-label="icon: upload" alt="upload" title="upload" />
  )
}

const IconDownload = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/cloud_download-24px.svg"
      aria-label="icon: download" alt="download" title="download" />
  )
}

const IconCopy = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/content_copy-24px.svg"
      aria-label="icon: copy" alt="copy" title="copy" />
  )
}

const IconFolder = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/folder-24px.svg"
      aria-label="icon: folder" alt="folder" title="folder" />
  )
}

const IconFolderNew = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/folder_new-24px.svg"
      aria-label="icon: create new folder" alt="create new folder"
      title="create new folder" />
  )
}

const IconDelete = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/delete-24px.svg"
      aria-label="icon: delete" alt="delete" title="delete" />
  )
}

const IconHistoryOff = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/history_toggle_off-24px.svg"
      aria-label="icon: history off" alt="history off" title="history off" />
  )
}

const IconHistory = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/history-24px.svg"
      aria-label="icon: history" alt="history" title="history" />
  )
}

const IconSpinningCircles = {
  view: (vnode) => (
    <img class={(vnode.attrs.class || "h-6") + " inline"}
      src="/static/icons/spinning-circles.svg"
      aria-label="icon: spinning circles" alt="spinning circles"
      title="spinning circles" />
  )
}

module.exports = {
  IconArchive,
  IconArchiveNew,
  IconUpload,
  IconDownload,
  IconCopy,
  IconFolder,
  IconFolderNew,
  IconDelete,
  IconHistoryOff,
  IconHistory,
  IconSpinningCircles,
}