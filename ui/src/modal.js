const m = require('mithril')

var Modal = {
    hidden: true,
    view: function (vnode) {
        return (
            <div id={vnode.attrs.id}>
                {vnode.state.hidden ? '' : (
                    <div class="fixed bottom-0 inset-x-0 px-4 pb-4 sm:inset-0 sm:flex sm:items-center sm:justify-center">
                        <div class="fixed inset-0 transition-opacity">
                            <div class="absolute inset-0 bg-gray-500 opacity-50"></div>
                        </div>

                        <div role="dialog" aria-modal="true" aria-labelledby="modal-headline"
                            class="bg-white rounded-md overflow-hidden shadow-xl transform transition-all sm:max-w-lg sm:w-full">
                            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                <div class="sm:flex sm:items-start">
                                    {vnode.attrs.icon ? (
                                        <div class={
                                            // 'bg-' + (vnode.attrs.colorPrimary || 'gray') + '-100 ' +
                                            'mx-auto flex-shrink-0 flex items-center justify-center'
                                            // + ' h-12 w-12 rounded-full'
                                            + ' sm:mx-0 sm:h-10 sm:w-10'
                                        }>
                                            {vnode.attrs.icon}
                                        </div>
                                    ) : ''}
                                    <div class="text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                                        {vnode.attrs.title ? (
                                            <h3 class="text-2xl leading-tight font-bold" id="modal-headline">
                                                {vnode.attrs.title}
                                            </h3>
                                        ) : ''}
                                        <div class="mt-2">
                                            {vnode.children}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                                <span class="flex w-full rounded-sm shadow-sm sm:ml-3 sm:w-auto">
                                    <button type="button" onclick={vnode.attrs.onclickPrimary || vnode.attrs.onclick}
                                        class={
                                            " bg-" + (vnode.attrs.colorPrimary || 'gray') + "-700"
                                            + " hover:bg-" + (vnode.attrs.colorPrimary || 'gray') + "-900"
                                            + " focus:border-" + (vnode.attrs.colorPrimary || 'gray') + "-700"
                                            + " focus:shadow-outline-" + (vnode.attrs.colorPrimary || 'gray')
                                            + " inline-flex justify-center w-full rounded-sm border border-transparent px-4 py-2 text-base leading-relaxed font-medium text-lg text-white shadow-sm focus:outline-none transition ease-in-out duration-150 sm:leading-relaxed"
                                        }
                                    >
                                        {vnode.attrs.valuePrimary || 'OK'}
                                    </button>
                                </span>
                                <span class="mt-3 flex w-full rounded-sm shadow-sm sm:mt-0 sm:w-auto">
                                    <button type="button" onclick={() => { vnode.state.hidden = true }}
                                        class="inline-flex justify-center w-full rounded-sm border border-gray-300 px-4 py-2 bg-white text-base leading-relaxed font-medium text-lg text-gray-700 shadow-sm hover:text-gray-500 focus:outline-none focus:border-blue-300 focus:shadow-outline-blue transition ease-in-out duration-150 sm:leading-relaxed"
                                    >
                                        {vnode.attrs.valueSecondary || 'Cancel'}
                                    </button>
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        )
    }
}

module.exports = { Modal }