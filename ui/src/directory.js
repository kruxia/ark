const m = require("mithril")

var Directory = {
    data: {},
    path: '',
    load: function (path) {
        path = path || ''
        return m.request({
            method: 'GET',
            url: 'http://localhost:8000/ark/' + path,
            withCredentials: false,
        }).then(function (result) {
            Directory.data = result
            Directory.path = path
        })
    },
}

var DirectoryList = {
    oninit: (vnode) => Directory.load(vnode.attrs.path),
    view: function () {
        if (Directory.data.files) {
            return (
                <div>
                    <table class="table-auto w-full">
                        <thead>
                            <tr>
                                <th class="border-b px-3 py-2 text-left">name</th>
                                <th class="border-b px-3 py-2 text-left">size</th>
                                <th class="border-b px-3 py-2 text-left">last modified</th>
                                <th class="border-b px-3 py-2 text-right">rev</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Directory.data.files.map((item, index) => {
                                var item_path = (
                                    Directory.path + '/' + item.path.name
                                ).replace(/^\//, '')
                                return (
                                    <tr key={index}>
                                        <td class="border-b px-3 py-2 text-left">
                                            <a href={item_path} onclick={(event) => {
                                                // TODO: Back button not working
                                                event.preventDefault()
                                                m.route.set(
                                                    '/:path...',
                                                    { path: item_path }
                                                )
                                                Directory.load(item_path)
                                            }}>
                                                {item.path.name}
                                            </a>
                                        </td>
                                        <td class="border-b px-3 py-2 text-left">
                                            {item.path.size}
                                        </td>
                                        <td class="border-b px-3 py-2 text-left">
                                            {
                                                item.version.date
                                                    .replace(/\.\d+/, '').replace('T', ' ')
                                                    .replace('+00:00', ' UTC')
                                            }
                                        </td>
                                        <td class="border-b px-3 py-2 text-right">
                                            {item.version.rev}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div >
            )
        } else {
            return "loading..."
        }
    }
}

module.exports = { DirectoryList }
