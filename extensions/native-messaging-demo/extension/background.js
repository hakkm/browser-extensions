const helper = chrome.runtime.connectNative('com.local.demo');

helper.onMessage.addListener(message => {
    console.log('Shortcut → Python → Brave → extension:', message);
    const reply = {ok: true, received: message};
    helper.postMessage(reply);
    console.log('Extension → Brave → Python → shortcut:', reply);
});

helper.onDisconnect.addListener(() => {
    console.log('Disconnected:', chrome.runtime.lastError?.message);
});

chrome.runtime.onStartup.addListener(() => {});
