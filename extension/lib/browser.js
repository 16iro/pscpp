/**
 * BrowserAdapter
 * chrome.* (callback) vs browser.* (Promise) 를 통일된 Promise API로 추상화.
 * 전역 변수 BrowserAPI として popup.js에서 사용.
 */
const BrowserAPI = (() => {
  // Firefox: 네이티브 browser.* (Promise 기반)
  if (typeof browser !== 'undefined' && browser.runtime) {
    return {
      tabs: {
        query: (q) => browser.tabs.query(q),
      },
      runtime: {
        sendNativeMessage: (host, msg) => browser.runtime.sendNativeMessage(host, msg),
      },
    };
  }

  // Chrome / Chromium: chrome.* (callback) → Promise 래핑
  return {
    tabs: {
      query: (q) => new Promise((resolve) => chrome.tabs.query(q, resolve)),
    },
    runtime: {
      sendNativeMessage: (host, msg) =>
        new Promise((resolve, reject) => {
          chrome.runtime.sendNativeMessage(host, msg, (res) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
            } else {
              resolve(res);
            }
          });
        }),
    },
  };
})();
