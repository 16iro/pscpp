const HOST = 'com.pscpp.host';

function tierName(level) {
  if (level === 0) return 'Unrated';
  const names  = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby'];
  const grades = ['V', 'IV', 'III', 'II', 'I'];
  return `${names[Math.floor((level - 1) / 5)]} ${grades[(level - 1) % 5]}`;
}

// BOJ 페이지 DOM에서 예제 입출력 추출 (executeScript로 페이지 컨텍스트에서 실행됨)
function extractSamples() {
  const samples  = [];
  const warnings = [];

  for (let i = 1; ; i++) {
    const inp = document.getElementById(`sample-input-${i}`);
    const exp = document.getElementById(`sample-output-${i}`);
    if (!inp && !exp) break;                          // 더 이상 없음
    if (inp && !exp) { warnings.push(`예제 ${i}: 출력 없음`); break; }
    if (!inp && exp) { warnings.push(`예제 ${i}: 입력 없음`); break; }
    samples.push({
      input:  inp.innerText.trimEnd(),
      output: exp.innerText.trimEnd(),
    });
  }
  return { samples, warnings };
}

async function init() {
  const [tab] = await BrowserAPI.tabs.query({ active: true, currentWindow: true });
  const match = tab?.url?.match(/acmicpc\.net\/problem\/(\d+)/);

  if (!match) return;

  const probId = match[1];

  // solved.ac API + 페이지 DOM 추출 병렬 실행
  const [apiRes, scriptRes] = await Promise.all([
    fetch(`https://solved.ac/api/v3/problem/show?problemId=${probId}`)
      .then(r => { if (!r.ok) throw new Error(`solved.ac ${r.status}`); return r.json(); }),
    BrowserAPI.scripting.executeScript({ target: { tabId: tab.id }, func: extractSamples }),
  ]).catch(e => {
    document.getElementById('status').textContent = `오류: ${e.message}`;
    return [null, null];
  });

  if (!apiRes) return;

  const data                     = apiRes;
  const { samples, warnings }    = scriptRes?.[0]?.result ?? { samples: [], warnings: [] };
  const tags                     = (data.tags ?? []).map(
    t => t.displayNames?.find(d => d.language === 'ko')?.name ?? t.key
  );

  document.getElementById('status').style.display = 'none';
  document.getElementById('info').style.display   = 'block';
  document.getElementById('prob-id').textContent    = probId;
  document.getElementById('prob-title').textContent = data.titleKo ?? data.title ?? '';
  document.getElementById('prob-tier').textContent  = tierName(data.level ?? 0);
  document.getElementById('prob-tags').textContent  = tags.join(', ') || '—';

  const sampleLabel = document.getElementById('prob-samples');
  if (sampleLabel) {
    let text = samples.length > 0 ? `${samples.length}개` : '없음';
    if (warnings.length) text += ` ⚠ ${warnings.join(', ')}`;
    sampleLabel.textContent = text;
  }

  const toggle    = document.getElementById('reset-toggle');
  const toggleRow = document.getElementById('toggle-row');
  const btn       = document.getElementById('btn');

  toggle.addEventListener('change', () => {
    const isReset = toggle.checked;
    toggleRow.classList.toggle('active', isReset);
    btn.classList.toggle('reset-mode', isReset);
  });

  btn.addEventListener('click', async () => {
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
        samples,
        reset:    toggle.checked,
      });

      if (res?.success) {
        result.className   = 'ok';
        result.textContent = `${res.action}: ${res.path} (예제 ${res.sample_count}개)`;
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
