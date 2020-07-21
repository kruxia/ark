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
                <div class="p-2 border shadow">
                    <h2>History</h2>
                    <table class="table-auto w-full">
                        <thead>
                            <tr>
                                <th class="align-bottom px-2 py-2 text-left w-12">
                                    rev
                                </th>
                                <th class="align-bottom px-2 py-2 text-left" colspan="2">
                                    details
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {
                                HistoryPanel.data.map((item, index) => {
                                    return (
                                        <tr key={index}>
                                            <td class="align-top px-2 py-2 border-t text-left w-12">
                                                {item.rev}
                                            </td>
                                            <td class="px-2 py-2 border-t">
                                                <table class="table-auto w-full">
                                                    <tbody>
                                                        <tr>
                                                            <td class="align-top text-left">
                                                                {item.date
                                                                    .replace(/\.\d+/, '').replace('T', ' ')
                                                                    .replace('+00:00', ' UTC')}
                                                            </td>
                                                            <td class="align-top text-left">
                                                                {item.author}
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td class="align-top text-left" colspan="2">
                                                                <p class="font-semibold">{item.message}</p>
                                                            </td>
                                                        </tr>
                                                        {item.paths.map((path, index) => {
                                                            return (
                                                                <tr>
                                                                    <td class="align-top text-left" colspan="2">
                                                                        <span title={ACTIONS[path.action]}>{path.action}</span>
                                                                        &#x2002;
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
                        </tbody >
                    </table >
                </div >
            )
        }
    }
}

module.exports = { HistoryPanel }