const m = require('mithril')
const { ACTIONS, PATH, PathLink } = require('./path')
const { IconSpinningCircles } = require('./icons')

var HistoryPanel = {
    data: [],
    visible: false,
    filesDisplayStyle: 'display:none;',
    waiting: false,
    oninit: function () {
    },
    load: function () {
        HistoryPanel.waiting = true
        if (PATH.query.has('rev')) {
            var rev = PATH.query.get('rev') + ':0'
        } else {
            var rev = 'HEAD:0'
        }
        var url = 'http://localhost:8000/ark/' + PATH.path + "?rev=" + rev
        console.log(url)
        m.request({
            method: 'GET',
            url: url,
            withCredentials: false,
        }).then((result) => {
            HistoryPanel.data = result.log
            HistoryPanel.waiting = false
            HistoryPanel.visible = true
        }).catch((error) => {
            console.log(error.response)
            HistoryPanel.waiting = false
        })
    },
    showHideFiles: function (event) {
        const vals = ['(show files)', '(hide files)']
        const filesDisplayStyles = {
            '(show files)': 'display:table-row;',
            '(hide files)': 'display:none;'
        }
        // toggle filesDisplayStyle to match the current command
        HistoryPanel.filesDisplayStyle = filesDisplayStyles[event.target.innerText]
        // cycle through the list of values
        event.target.innerText = vals[(vals.indexOf(event.target.innerText) + 1) % vals.length]
    },
    view: function () {
        if (!HistoryPanel.waiting && HistoryPanel.visible == true && HistoryPanel.data.length > 0) {
            return (
                <div class="border p-2 mb-2 shadow-lg">
                    <h2>History</h2>
                    <HistoryPanelTable />
                </div >
            )
        }
    }
}

var HistoryPanelTable = {
    view: function () {
        return (
            <table class="table-auto w-full">
                <thead>
                    <tr>
                        <th class="align-bottom pr-2 py-2 text-left w-12">
                            rev
                        </th>
                        <th class="align-bottom py-2 text-left" colspan="2">
                            <span class="mr-2">details</span>
                            <button onclick={HistoryPanel.showHideFiles}>
                                (show files)
                            </button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <HistoryPanelBody />
                </tbody >
            </table >
        )
    }
}

var HistoryPanelBody = {
    view: function () {
        return (
            HistoryPanel.data.map((item, index) => {
                var query = new URLSearchParams('?rev=' + item.rev)
                return (
                    <tr key={index}>
                        <td class="align-top pr-2 py-2 border-t text-left w-8">
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
                                    <tr style={HistoryPanel.filesDisplayStyle}>
                                        <td class="align-top text-left" colspan="2">
                                            <table class="table-auto w-full -mx-px mt-2">
                                                {item.paths.map((path) => {
                                                    return (
                                                        <tr>
                                                            <td class="align-text-top font-medium pb-1 pr-2 text-left text-xs uppercase w-6">
                                                                {ACTIONS[path.action]}
                                                            </td>
                                                            <td class="align-text-top pb-1 text-left" style="word-break:break-word;">
                                                                {decodeURI(path.relpath)}
                                                            </td>
                                                        </tr>
                                                    )
                                                })}
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                )
            })
        )
    }
}



module.exports = { HistoryPanel }