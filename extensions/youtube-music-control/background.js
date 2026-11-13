function musicState() {
    const media = document.querySelector('video, audio');
    if (!media || !media.currentSrc)
        return null;
    return {playing: !media.paused && !media.ended};
}

async function controlMusic(action) {
    const media = document.querySelector('video, audio');
    if (!media || !media.currentSrc)
        throw new Error('No song loaded in YouTube Music');
    if (action === 'pause')
        media.pause();
    else
        await media.play();
}

async function toggleMusic() {
    const tabs = await chrome.tabs.query({url: 'https://music.youtube.com/*'});
    const players = [];
    for (const tab of tabs) {
        try {
            const results = await chrome.scripting.executeScript({
                target: {tabId: tab.id}, func: musicState,
            });
            if (results[0]?.result)
                players.push({tab, ...results[0].result});
        } catch (error) {
            console.warn('Cannot inspect YouTube Music tab', error);
        }
    }
    if (!players.length)
        throw new Error('Open YouTube Music and load a song first');
    const playing = players.filter(player => player.playing);
    const targets = playing.length ? playing : [players.sort(
        (first, second) => (second.tab.lastAccessed || 0) - (first.tab.lastAccessed || 0)
    )[0]];
    const action = playing.length ? 'pause' : 'play';
    await Promise.all(targets.map(player => chrome.scripting.executeScript({
        target: {tabId: player.tab.id}, func: controlMusic, args: [action],
    })));
    await chrome.action.setBadgeText({text: ''});
    await chrome.action.setTitle({title: 'Play / pause YouTube Music only'});
    return {ok: true};
}

let pending = Promise.resolve();
function enqueueToggle() {
    pending = pending.then(toggleMusic).catch(async error => {
        console.error(error);
        await chrome.action.setBadgeText({text: '!'});
        await chrome.action.setTitle({title: error.message});
        return {ok: false, error: error.message};
    });
    return pending;
}

chrome.action.onClicked.addListener(enqueueToggle);

let desktopPort;
function connectDesktop() {
    if (desktopPort)
        return;
    const port = chrome.runtime.connectNative('com.local.youtube_music');
    desktopPort = port;
    port.onMessage.addListener(async message => {
        if (message.action !== 'toggle')
            return;
        const result = await enqueueToggle();
        if (desktopPort === port)
            port.postMessage(result);
    });
    port.onDisconnect.addListener(() => {
        desktopPort = null;
        if (chrome.runtime.lastError)
            console.warn(chrome.runtime.lastError.message);
    });
}

chrome.runtime.onStartup.addListener(connectDesktop);
chrome.runtime.onInstalled.addListener(connectDesktop);
connectDesktop();
