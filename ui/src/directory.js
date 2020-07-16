const m = require("mithril")

var Directory = {
    data: {},
    load: function () {
        return m.request({
            method: 'GET',
            url: 'http://localhost:8000/ark/test1',
            withCredentials: false,
        }).then(function (result) {
            Directory.data = result
        })
    },
}

var DirectoryList = {
    oninit: Directory.load,
    view: function () {
        if (Directory.data.info && Directory.data.files) {
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
                            {Directory.data.files.map((value, index) => {
                                return (
                                    <tr key="{index}">
                                        <td class="border-b px-3 py-2 text-left">
                                            <a href={value.path.url}>{value.path.name}</a>
                                        </td>
                                        <td class="border-b px-3 py-2 text-left">
                                            {value.path.size}
                                        </td>
                                        <td class="border-b px-3 py-2 text-left">
                                            {
                                                value.version.date
                                                    .replace(/\.\d+/, '').replace('T', ' ')
                                                    .replace('+00:00', ' UTC')
                                            }
                                        </td>
                                        <td class="border-b px-3 py-2 text-right">
                                            {value.version.rev}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            )
        } else {
            return "loading..."
        }
    }
}

module.exports = { DirectoryList }
