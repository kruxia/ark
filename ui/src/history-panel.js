const m = require('mithril')
const { ACTIONS, PATH, PathLink } = require('./path')

var HistoryPanel = {
    data: [],
    visible: false,
    oninit: function () {
    },
    load: function () {
        if (PATH.query.has('rev')) {
            var rev = PATH.query.get('rev') + ':0'
        } else {
            var rev = 'HEAD:0'
        }
        var url = 'http://localhost:8000/ark/' + PATH.path + "?rev=" + rev
        m.request({
            method: 'GET',
            url: url,
            withCredentials: false,
        }).then((result) => {
            HistoryPanel.data = result.log
        }).catch((error) => {
            console.log(error.response)
        })
    },
    view: function () {
        if (HistoryPanel.visible == true && HistoryPanel.data.length > 0) {
            return (
                <div class="p-2 shadow">
                    <h2>History</h2>
                    <table class="table-auto w-full">
                        <thead>
                            <tr>
                                <th class="align-bottom pr-2 py-2 text-left w-12">
                                    rev
                                </th>
                                <th class="align-bottom py-2 text-left" colspan="2">
                                    details
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {
                                HistoryPanel.data.map((item, index) => {
                                    var query = new URLSearchParams('?rev=' + item.rev)
                                    return (
                                        <tr key={index}>
                                            <td class="align-top pr-2 py-2 border-t text-left w-12">
                                                <PathLink path={'/' + PATH.path} query={query} name={item.rev} />
                                            </td>
                                            <td class="py-2 border-t">
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