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
                        <tbody>
                            {
                                HistoryPanel.data.map((item, index) => {
                                    return (
                                        <>
                                        <tr key={index+'a'}>
                                            <td class="align-top px-2 pt-2 border-t w-20 text-left">
                                                rev {item.rev}
                                            </td>
                                            <td class="align-top px-2 pt-2 border-t text-left">
                                                {item.date
                                                    .replace(/\.\d+/, '').replace('T', ' ')
                                                    .replace('+00:00', ' UTC')}
                                            </td>
                                        </tr>
                                        <tr key={index+'b'}>
                                            <td colspan="2" class="align-top px-2 pb-2 text-left">
                                                <p class="font-semibold">{item.message }</p>
                                                <table class="table-auto w-full">
                                                    <tbody>
                                                        {item.paths.map((path, index) => {
                                                            return (
                                                                <tr>
                                                                    <td class="align-top w-20">
                                                                        {ACTIONS[path.action]}
                                                                    </td>
                                                                    <td class="align-top">
                                                                        {decodeURI(path.name)}
                                                                    </td>
                                                                </tr>
                                                            )
                                                        })}
                                                    </tbody>
                                                </table>
                                            </td>
                                        </tr>
                                        </>
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