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

    if os.path.exists(dest):
        return {'success': False, 'error': f'이미 존재함: {platform}/{prob_id}'}

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

    # 빈 테스트 파일
    open(os.path.join(dest, 'input.txt'),    'w').close()
    open(os.path.join(dest, 'expected.txt'), 'w').close()

    rel = f'{platform}/{prob_id}'
    return {'success': True, 'path': rel}


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
