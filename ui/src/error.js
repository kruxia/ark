const m = require('mithril')
const { PATH, Breadcrumbs } = require('./path')

var ErrorView = {
  view: function () {
    return (
      <div class="leading-tight">
        <div class="text-2xl font-light">
          <Breadcrumbs />
        </div>
        <h1 class="mx-2 mt-2 text-4xl font-black">{PATH.error.code}</h1>
        <p class="mx-2 uppercase">{PATH.error.message}</p>
        <div class="mx-2 my-2">
          {/* An HTTP status dog to brighten your day */}
          <img src={'https://httpstatusdogs.com/img/' + PATH.error.code + '.jpg'}
            alt={'HTTP ' + PATH.error.code + ' dog'} />
        </div>
      </div>
    )
  }
}

module.exports = { ErrorView }
