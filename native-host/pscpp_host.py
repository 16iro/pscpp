#!/usr/bin/env python3
"""
pscpp Native Messaging Host
Chrome 익스텐션으로부터 메시지를 받아 문제 폴더를 생성한다.

프로토콜: stdin/stdout, 메시지마다 4바이트 LE 길이 + UTF-8 JSON
"""

import json
import os
import shutil
import struct
import sys

# 이 스크립트 기준으로 레포 루트 계산 (native-host/ 의 상위)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 메시지 I/O ────────────────────────────────────────────────

def read_message() -> dict:
    raw_len = sys.stdin.buffer.read(4)
    if len(raw_len) < 4:
        sys.exit(0)
    msg_len = struct.unpack('<I', raw_len)[0]
    raw = sys.stdin.buffer.read(msg_len)
    return json.loads(raw.decode('utf-8'))


def send_message(obj: dict) -> None:
    data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('<I', len(data)))
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


# ── 헬퍼 ─────────────────────────────────────────────────────

import re as _re

def _parse_time_sec(time_str: str | None) -> float:
    """'2 초', '0.5 초 (추가 시간 없음)' 등에서 초 단위 float 추출."""
    if not time_str:
        return 2.0
    m = _re.search(r'([\d.]+)\s*초', time_str)
    return float(m.group(1)) if m else 2.0


def _write_info(dest: str, msg: dict) -> None:
    stmt = msg.get('statement') or {}
    info = {
        'title':      msg.get('title', ''),
        'tier':       msg.get('tier', ''),
        'tags':       msg.get('tags', []),
        'time_limit': msg.get('time_limit'),
        'mem_limit':  msg.get('mem_limit'),
        'time_limit_sec': _parse_time_sec(msg.get('time_limit')),
        'statement': {
            'description': stmt.get('description', ''),
            'input':       stmt.get('input', ''),
            'output':      stmt.get('output', ''),
        },
    }
    with open(os.path.join(dest, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


def _write_samples(dest: str, samples: list):
    """
    예제 입출력을 tc/N.in · tc/N.out 파일로 개별 저장.
    기존 tc/ 디렉토리가 있으면 비우고 새로 작성한다.
    """
    tc_dir = os.path.join(dest, 'tc')
    if os.path.exists(tc_dir):
        shutil.rmtree(tc_dir)
    os.makedirs(tc_dir)

    for i, s in enumerate(samples, 1):
        inp = s.get('input', '')
        out = s.get('output', '')
        with open(os.path.join(tc_dir, f'{i}.in'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(inp if inp.endswith('\n') else inp + '\n')
        with open(os.path.join(tc_dir, f'{i}.out'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(out if out.endswith('\n') else out + '\n')


# ── 액션 핸들러 ───────────────────────────────────────────────

def handle_new_prob(msg: dict) -> dict:
    platform = msg.get('platform', 'BOJ')
    prob_id  = str(msg.get('id', ''))
    title    = msg.get('title', '')
    tier     = msg.get('tier', '')
    tags     = msg.get('tags', [])

    if not prob_id:
        return {'success': False, 'error': 'id 필드 없음'}

    dest = os.path.join(REPO_ROOT, platform, prob_id)

    samples  = msg.get('samples', [])
    do_reset = msg.get('reset', False)
    exists   = os.path.exists(dest)

    if exists and not do_reset:
        # 예제 + 메타데이터 갱신 (main.cpp · README 유지)
        _write_samples(dest, samples)
        _write_info(dest, msg)
        return {'success': True, 'action': '예제 갱신',
                'path': f'{platform}/{prob_id}', 'sample_count': len(samples)}

    if exists and do_reset:
        shutil.rmtree(dest)

    os.makedirs(dest)

    # main.cpp — 템플릿 복사
    src_cpp = os.path.join(REPO_ROOT, 'templates', 'template.cpp')
    shutil.copy(src_cpp, os.path.join(dest, 'main.cpp'))

    # README.md — 템플릿 치환
    src_md = os.path.join(REPO_ROOT, 'templates', 'template.md')
    with open(src_md, encoding='utf-8') as f:
        md = f.read()

    md = (md
          .replace('{번호}',  prob_id)
          .replace('{제목}',  title)
          .replace('{solved.ac 티어}', tier)
          .replace('{태그1}, {태그2}', ', '.join(tags) if tags else '—')
          .replace('{태그1}', tags[0] if tags else '—')
          )

    with open(os.path.join(dest, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(md)

    _write_samples(dest, samples)
    _write_info(dest, msg)

    action = '초기화' if (exists and do_reset) else '생성'
    return {'success': True, 'action': action,
            'path': f'{platform}/{prob_id}', 'sample_count': len(samples)}


# ── 메인 루프 ─────────────────────────────────────────────────

HANDLERS = {
    'new_prob': handle_new_prob,
}

if __name__ == '__main__':
    msg = read_message()
    action = msg.get('action')
    handler = HANDLERS.get(action)
    if handler:
        send_message(handler(msg))
    else:
        send_message({'success': False, 'error': f'알 수 없는 action: {action}'})
