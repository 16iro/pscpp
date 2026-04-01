const HOST = 'com.pscpp.host';

function tierName(level) {
  if (level === 0) return 'Unrated';
  const names  = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby'];
  const grades = ['V', 'IV', 'III', 'II', 'I'];
  return `${names[Math.floor((level - 1) / 5)]} ${grades[(level - 1) % 5]}`;
}

async function init() {
  const [tab] = await BrowserAPI.tabs.query({ active: true, currentWindow: true });
  const match = tab?.url?.match(/acmicpc\.net\/problem\/(\d+)/);

  if (!match) return;

  const probId = match[1];

  let data;
  try {
    const res = await fetch(`https://solved.ac/api/v3/problem/show?problemId=${probId}`);
    if (!res.ok) throw new Error(`solved.ac ${res.status}`);
    data = await res.json();
  } catch (e) {
    document.getElementById('status').textContent = `solved.ac 오류: ${e.message}`;
    return;
  }

  const tags = (data.tags ?? []).map(
    t => t.displayNames?.find(d => d.language === 'ko')?.name ?? t.key
  );

  document.getElementById('status').style.display = 'none';
  document.getElementById('info').style.display   = 'block';
  document.getElementById('prob-id').textContent    = probId;
  document.getElementById('prob-title').textContent = data.titleKo ?? data.title ?? '';
  document.getElementById('prob-tier').textContent  = tierName(data.level ?? 0);
  document.getElementById('prob-tags').textContent  = tags.join(', ') || '—';

  document.getElementById('btn').addEventListener('click', async () => {
    const btn    = document.getElementById('btn');
    const result = document.getElementById('result');
    btn.disabled = true;
    result.textContent = '';

    try {
      const res = await BrowserAPI.runtime.sendNativeMessage(HOST, {
        action:   'new_prob',
        platform: 'BOJ',
        id:       probId,
        title:    data.titleKo ?? data.title ?? '',
        tier:     tierName(data.level ?? 0),
        tags,
      });

      if (res?.success) {
        result.className   = 'ok';
        result.textContent = `생성됨: ${res.path}`;
      } else {
        throw new Error(res?.error ?? '알 수 없는 오류');
      }
    } catch (e) {
      result.className   = 'err';
      result.textContent = e.message;
      btn.disabled = false;
    }
  });
}

init();
