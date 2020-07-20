const m = require('mithril')
const { ACTIONS, PATH } = require('./path')

var HistoryPanel = {
    data: [],
    visible: false,
    oninit: function () {
    },
    load: function () {
        return m.request({
            method: 'GET',
            url: 'http://localhost:8000/ark/' + PATH.path + "?rev=HEAD:0",
            withCredentials: false,
        }).then(function (result) {
            HistoryPanel.data = result.log
        })
    },
    view: function () {
        if (HistoryPanel.visible == true && HistoryPanel.data.length > 0) {
            return (
                <div class="m-2 p-2 border shadow">
                    <h2>History</h2>
                    <table class="table-auto w-full">
                        <thead>
                            <tr>
                                <th class="border-b px-2 py-2 text-left w-8">rev</th>
                                <th class="border-b px-2 py-2 text-left w-56">date</th>
                                <th class="border-b px-2 py-2 text-left">changes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {
                                HistoryPanel.data.map((item, index) => {
                                    return (
                                        <tr key={index}>
                                            <td class="align-top border-b px-2 py-2 text-left">
                                                {item.rev}
                                            </td>
                                            <td class="align-top border-b px-2 py-2 text-left">
                                                {item.date
                                                    .replace(/\.\d+/, '').replace('T', ' ')
                                                    .replace('+00:00', ' UTC')}
                                            </td>
                                            <td class="align-top border-b px-2 py-2 text-left">
                                                <p class="font-semibold">{item.message || ' '}</p>
                                                <table class="table-auto w-full">
                                                    <tbody>
                                                        {item.paths.map((path, index) => {
                                                            return (
                                                                <tr>
                                                                    <td class="align-top w-20 border-t">
                                                                        {ACTIONS[path.action]}
                                                                    </td>
                                                                    <td class="align-top border-t">
                                                                        {decodeURI(path.name)}
                                                                    </td>
                                                                </tr>
                                                            )
                                                        })}
                                                    </tbody>
                                                </table>
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
}

module.exports = { HistoryPanel }