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
            m.render(Directory)
        })
    },
}

var DirectoryList = {
    oninit: Directory.load,
    view: function () {
        return Directory.data.info && Directory.data.files && (
            <div>
                <h1>{Directory.data.info.path.name}</h1>
                <table>
                    <thead>
                        <tr>
                            <th>name</th>
                            <th>size</th>
                            <th>last modified</th>
                            <th>rev</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Directory.data.files.map((value, index) => {
                            return (
                                <tr key="{index}">
                                    <td><a href={value.path.url}>{value.path.name}</a></td>
                                    <td>{value.path.size}</td>
                                    <td>{value.version.date}</td>
                                    <td>{value.version.rev}</td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        ) || "loading..."
    }
}

module.exports = { DirectoryList }
