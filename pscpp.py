#!/usr/bin/env python3
"""
pscpp —unified CLI

사용법:
  python pscpp.py setup
  python pscpp.py new    BOJ 1234
  python pscpp.py build  BOJ 1234
  python pscpp.py test   BOJ 1234
  python pscpp.py submit BOJ 1234 ["접근 방법 요약"]
"""

import argparse
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

# Windows CP949 환경에서 UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))

# Windows NTSTATUS / Unix signal exit code 설명
_EXIT_CODE_NAMES: dict[int, str] = {
    # Windows NTSTATUS (unsigned 32-bit, Python receives as signed-extended int)
    0xC0000005: 'ACCESS_VIOLATION',
    0xC0000374: 'HEAP_CORRUPTION',
    0xC0000409: 'STACK_BUFFER_OVERRUN',
    0xC00000FD: 'STACK_OVERFLOW',
    0xC0000094: 'INTEGER_DIVIDE_BY_ZERO',
    0xC0000095: 'INTEGER_OVERFLOW',
    0xC000008E: 'FLOAT_DIVIDE_BY_ZERO',
    0xC0000096: 'PRIVILEGED_INSTRUCTION',
    0xC000001D: 'ILLEGAL_INSTRUCTION',
    0xC0000006: 'IN_PAGE_ERROR',
    # Windows CRT exit codes
    3: 'abort() (assert/runtime check failure)',
    # Unix signals (128 + signal)
    134: 'SIGABRT (abort/assert)',
    136: 'SIGFPE (float exception)',
    139: 'SIGSEGV (segfault)',
    138: 'SIGBUS (bus error)',
}

def _exit_code_name(code: int) -> str:
    name = _EXIT_CODE_NAMES.get(code & 0xFFFFFFFF) or _EXIT_CODE_NAMES.get(code)
    return f' ({name})' if name else ''


# ── .env 로더 ─────────────────────────────────────────────────

def load_env() -> dict:
    env = {}
    path = os.path.join(ROOT, '.env')
    if not os.path.exists(path):
        return env
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            k, _, v = line.partition('=')
            env[k.strip()] = v.strip()
    return env


def compiler(env: dict) -> str:
    return env.get('COMPILER', 'gcc').lower()


def is_windows() -> bool:
    return platform.system() == 'Windows'


# ── cmake 헬퍼 ────────────────────────────────────────────────

def _build_env(env: dict) -> dict:
    """cmake / 바이너리 실행에 필요한 PATH가 담긴 환경변수 반환."""
    run_env = os.environ.copy()
    if is_windows() and compiler(env) != 'msvc':
        mingw_bin = os.path.join(env.get('MSYS2_ROOT', r'C:\msys64'), 'mingw64', 'bin')
        run_env['PATH'] = mingw_bin + os.pathsep + run_env.get('PATH', '')
    return run_env


def cmake_configure(build_dir: str, env: dict) -> None:
    args = ['cmake', '-S', ROOT, '-B', build_dir]
    if compiler(env) == 'msvc':
        pass  # MSVC: cmake 가 Visual Studio 자동 감지
    else:
        if is_windows():
            args += ['-G', 'MinGW Makefiles']
        args += ['-DCMAKE_BUILD_TYPE=Release']
    result = subprocess.run(args, capture_output=True, text=True, env=_build_env(env))
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        raise SystemExit(f'cmake configure 실패 (exit {result.returncode})')


def cmake_build(build_dir: str, target: str, env: dict) -> None:
    args = ['cmake', '--build', build_dir, '--target', target]
    if compiler(env) == 'msvc':
        args += ['--config', 'Release']
    else:
        args += ['--', '-j4']
    subprocess.run(args, check=True, env=_build_env(env))


def find_binary(build_dir: str, plat: str, prob: str) -> str:
    target = f'{plat}_{prob}'
    base   = os.path.join(build_dir, plat, prob)
    for candidate in [
        os.path.join(base, target + '.exe'),
        os.path.join(base, 'Release', target + '.exe'),
        os.path.join(base, target),
    ]:
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(f'Binary not found: {target}')


# ── setup ─────────────────────────────────────────────────────

SKILL_FRONTMATTER = {
    'claude': {
        'hint': (
            '---\n'
            'name: hint\n'
            'description: "competitive programming 힌트 제공 (progress / errline / errfunc / counter)"\n'
            'argument-hint: "{platform} {problem_number} {hint_type}"\n'
            'user-invocable: true\n'
            '---\n\n'
        ),
        'code-review': (
            '---\n'
            'name: code-review\n'
            'description: "AC 코드 + README 기반 풀이 리뷰 (코드 품질 · 문서 완성도 평가)"\n'
            'argument-hint: "{platform} {problem_number}"\n'
            'user-invocable: true\n'
            '---\n\n'
        ),
    },
    'gemini': {
        'hint': '',       # Gemini는 프론트매터 없이 본문만
        'code-review': '',
    },
}

SKILL_TARGETS = {
    'claude': lambda name: os.path.join(ROOT, '.claude', 'skills', name, 'SKILL.md'),
    'gemini': lambda name: os.path.join(ROOT, '.gemini', 'instructions', f'{name}.md'),
}


def _build_skills() -> None:
    """templates/skills/ 의 공유 본문에 LLM별 프론트매터를 붙여 스킬 파일 생성."""
    skills_src = os.path.join(ROOT, 'templates', 'skills')
    if not os.path.isdir(skills_src):
        return

    for src_file in os.listdir(skills_src):
        if not src_file.endswith('.md'):
            continue
        skill_name = src_file.removesuffix('.md')

        with open(os.path.join(skills_src, src_file), encoding='utf-8') as f:
            body = f.read()

        for llm, targets in SKILL_TARGETS.items():
            frontmatter = SKILL_FRONTMATTER.get(llm, {}).get(skill_name, '')
            dest = targets(skill_name)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'w', encoding='utf-8', newline='\n') as f:
                f.write(frontmatter + body)

    print('스킬 빌드 완료 (claude, gemini)')


def cmd_setup(env: dict) -> None:
    # git hooks 등록
    subprocess.run(
        ['git', '-C', ROOT, 'config', 'core.hooksPath', '.githooks'],
        check=True,
    )
    hook = os.path.join(ROOT, '.githooks', 'post-checkout')
    if os.path.exists(hook):
        os.chmod(hook, 0o755)
    print('git hooks 등록 완료')

    # 스킬 빌드
    _build_skills()

    # .env 생성 (이미 있으면 스킵)
    env_path = os.path.join(ROOT, '.env')
    if os.path.exists(env_path):
        print('.env 이미 존재합니다. 스킵.')
        return

    # MSYS2 경로 탐색
    msys2_root = r'C:\msys64'
    for c in [r'C:\msys64', r'C:\msys2']:
        if os.path.isfile(os.path.join(c, 'usr', 'bin', 'bash.exe')):
            msys2_root = c
            break
    else:
        if is_windows():
            print('경고: MSYS2를 찾을 수 없습니다. .env의 MSYS2_ROOT를 직접 수정하세요.')

    # 컴파일러 감지
    comp = 'msvc' if shutil.which('cl') else 'gcc'

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(f'MSYS2_ROOT={msys2_root}\n')
        f.write(f'COMPILER={comp}\n')

    print(f'.env 생성 완료  MSYS2_ROOT={msys2_root}  COMPILER={comp}')


# ── new ───────────────────────────────────────────────────────

def cmd_new(plat: str, prob: str) -> None:
    dest = os.path.join(ROOT, plat, prob)
    if os.path.exists(dest):
        print(f'이미 존재함: {plat}/{prob}')
        return

    os.makedirs(dest)

    shutil.copy(
        os.path.join(ROOT, 'templates', 'template.cpp'),
        os.path.join(dest, 'main.cpp'),
    )
    with open(os.path.join(ROOT, 'templates', 'template.md'), encoding='utf-8') as f:
        md = f.read().replace('{번호}', prob)
    with open(os.path.join(dest, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(md)

    os.makedirs(os.path.join(dest, 'tc'), exist_ok=True)

    print(f'생성됨: {plat}/{prob}')


# ── build ─────────────────────────────────────────────────────

def cmd_build(plat: str, prob: str, env: dict) -> None:
    build_dir = os.path.join(ROOT, 'build')
    target    = f'{plat}_{prob}'

    cmake_configure(build_dir, env)
    cmake_build(build_dir, target, env)

    binary = find_binary(build_dir, plat, prob)
    print(f'빌드 완료: {binary}')


# ── test ──────────────────────────────────────────────────────

def cmd_test(plat: str, prob: str, env: dict) -> None:
    build_dir = os.path.join(ROOT, 'build')
    prob_dir  = os.path.join(ROOT, plat, prob)
    target    = f'{plat}_{prob}'

    cmake_configure(build_dir, env)
    cmake_build(build_dir, target, env)
    binary = find_binary(build_dir, plat, prob)

    tc_dir = os.path.join(prob_dir, 'tc')

    # info.json 에서 시간제한 읽기 (없으면 기본 5초)
    info_path = os.path.join(prob_dir, 'info.json')
    time_limit_sec = 5.0
    if os.path.exists(info_path):
        with open(info_path, encoding='utf-8') as f:
            info = json.load(f)
        time_limit_sec = float(info.get('time_limit_sec', 5.0))
        print(f'시간제한: {info.get("time_limit", f"{time_limit_sec}초")} '
              f'(타임아웃: {time_limit_sec}s)')

    # tc/ 에서 N.in 파일을 숫자 순으로 수집
    if not os.path.isdir(tc_dir):
        print('tc/ 디렉토리 없음 —스킵')
        return

    cases = sorted(
        [int(f.removesuffix('.in')) for f in os.listdir(tc_dir) if f.endswith('.in')],
    )
    if not cases:
        print('tc/ 에 테스트케이스 없음 —스킵')
        return

    passed = failed = 0
    run_env = _build_env(env)

    for n in cases:
        in_path  = os.path.join(tc_dir, f'{n}.in')
        out_path = os.path.join(tc_dir, f'{n}.out')

        if not os.path.exists(out_path):
            print(f'⚠ SKIP [케이스 {n}] — {n}.out 없음')
            continue

        with open(out_path, encoding='utf-8') as f:
            expect = f.read().strip()

        tmp_out = tempfile.mktemp(suffix='.out')
        try:
            with open(in_path, 'rb') as sin, open(tmp_out, 'wb') as sout:
                try:
                    proc = subprocess.run([binary], stdin=sin, stdout=sout,
                                          stderr=subprocess.DEVNULL, env=run_env,
                                          timeout=time_limit_sec, check=False)
                except subprocess.TimeoutExpired:
                    print(f'⏱ TLE [케이스 {n}] — {time_limit_sec}s 초과')
                    failed += 1
                    continue

            if os.path.exists(tmp_out):
                with open(tmp_out, 'rb') as f:
                    actual = f.read().decode('utf-8', errors='replace').replace('\r\n', '\n').strip()
            else:
                actual = ''
        finally:
            if os.path.exists(tmp_out):
                os.unlink(tmp_out)

        if proc.returncode != 0:
            print(f'✗ FAIL [케이스 {n}] (exit code {proc.returncode}{_exit_code_name(proc.returncode)})')
            failed += 1
        elif actual == expect:
            print(f'✓ PASS [케이스 {n}]')
            passed += 1
        else:
            print(f'✗ FAIL [케이스 {n}]')
            for line in _diff_lines(expect, actual):
                print(f'  {line}')
            failed += 1

    print(f'\n결과: {passed} passed, {failed} failed —{plat}/{prob}')
    sys.exit(0 if failed == 0 else 1)


def _diff_lines(expected: str, actual: str) -> list[str]:
    exp_lines = expected.splitlines()
    act_lines = actual.splitlines()
    out = []
    for i, (e, a) in enumerate(zip(exp_lines, act_lines)):
        mark = '  ' if e == a else '!!'
        out.append(f'{mark} [{i+1}] expected={e!r}  actual={a!r}')
    if len(exp_lines) != len(act_lines):
        out.append(f'!! 줄 수 다름: expected={len(exp_lines)}, actual={len(act_lines)}')
    return out


# ── submit ────────────────────────────────────────────────────

def cmd_submit(plat: str, prob: str, message: str) -> None:
    rel_dir = f'{plat}/{prob}'

    diff = subprocess.run(
        ['git', '-C', ROOT, 'diff', '--quiet', 'HEAD', '--', rel_dir],
        capture_output=True,
    )
    diff_cached = subprocess.run(
        ['git', '-C', ROOT, 'diff', '--quiet', '--cached', 'HEAD', '--', rel_dir],
        capture_output=True,
    )
    untracked = subprocess.run(
        ['git', '-C', ROOT, 'ls-files', '--others', '--exclude-standard', '--', rel_dir],
        capture_output=True, text=True, encoding='utf-8',
    )
    if diff.returncode == 0 and diff_cached.returncode == 0 and not untracked.stdout.strip():
        print(f'변경사항 없음: {rel_dir}')
        return

    log = subprocess.run(
        ['git', '-C', ROOT, 'log', '--oneline', '--', rel_dir],
        capture_output=True, text=True, encoding='utf-8',
    )
    attempt = len(log.stdout.strip().splitlines()) + 1

    commit_msg = f'{plat}/{prob}: attempt #{attempt}'
    if message:
        commit_msg += f' - {message}'

    targets = [f'{rel_dir}/{f}' for f in
               ('main.cpp', 'README.md', 'info.json')
               if os.path.exists(os.path.join(ROOT, rel_dir, f))]
    tc_dir = os.path.join(ROOT, rel_dir, 'tc')
    if os.path.isdir(tc_dir):
        targets.append(f'{rel_dir}/tc')
    subprocess.run(['git', '-C', ROOT, 'add'] + targets, check=True)
    subprocess.run(['git', '-C', ROOT, 'commit', '-m', commit_msg], check=True, capture_output=True, encoding='utf-8')
    subprocess.run(['git', '-C', ROOT, 'push'], check=True)
    print(f'\nCommitted & pushed: {commit_msg}')
    print('→ BOJ에 직접 제출하세요.')


# ── review-commit ────────────────────────────────────────────

def cmd_review_commit(plat: str, prob: str) -> None:
    rel_dir = f'{plat}/{prob}'
    readme  = os.path.join(ROOT, rel_dir, 'README.md')

    if not os.path.exists(readme):
        print(f'README.md 없음: {rel_dir}')
        return

    diff = subprocess.run(
        ['git', '-C', ROOT, 'diff', '--quiet', 'HEAD', '--', os.path.join(rel_dir, 'README.md')],
        capture_output=True,
    )
    if diff.returncode == 0:
        print(f'README.md 변경사항 없음: {rel_dir}')
        return

    commit_msg = f'{plat}/{prob}: code review by AI'
    subprocess.run(['git', '-C', ROOT, 'add', os.path.join(rel_dir, 'README.md')], check=True)
    subprocess.run(['git', '-C', ROOT, 'commit', '-m', commit_msg], check=True, capture_output=True, encoding='utf-8')
    subprocess.run(['git', '-C', ROOT, 'push'], check=True)
    print(f'Committed & pushed: {commit_msg}')


# ── add-tc ───────────────────────────────────────────────────

def _unescape(s: str) -> str:
    r"""리터럴 \n · \t 를 실제 개행·탭으로 변환. 복붙 줄바꿈은 그대로 유지."""
    return s.replace('\\n', '\n').replace('\\t', '\t')


def _read_block(label: str) -> str:
    """인터랙티브 입력. 빈 줄 입력 시 종료."""
    print(f'[{label}] (빈 줄로 종료):')
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == '':
            break
        lines.append(line)
    return '\n'.join(lines)


def cmd_add_tc(plat: str, prob: str, tc_in: str | None, tc_out: str | None) -> None:
    tc_dir = os.path.join(ROOT, plat, prob, 'tc')
    os.makedirs(tc_dir, exist_ok=True)

    # 인터랙티브 모드
    if tc_in is None or tc_out is None:
        tc_in  = _read_block('예제 입력')
        tc_out = _read_block('예제 출력')
    else:
        tc_in  = _unescape(tc_in)
        tc_out = _unescape(tc_out)

    # 다음 번호 결정
    existing = [int(f.removesuffix('.in')) for f in os.listdir(tc_dir) if f.endswith('.in')]
    n = max(existing, default=0) + 1

    with open(os.path.join(tc_dir, f'{n}.in'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(tc_in if tc_in.endswith('\n') else tc_in + '\n')
    with open(os.path.join(tc_dir, f'{n}.out'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(tc_out if tc_out.endswith('\n') else tc_out + '\n')

    print(f'추가됨: {plat}/{prob}/tc/{n}.in · {n}.out')


# ── clean ────────────────────────────────────────────────────

def cmd_clean(plat: str) -> None:
    plat_dir = os.path.join(ROOT, plat)
    if not os.path.isdir(plat_dir):
        print(f'플랫폼 디렉토리 없음: {plat}')
        return

    targets = []
    for name in sorted(os.listdir(plat_dir)):
        prob_dir = os.path.join(plat_dir, name)
        if not os.path.isdir(prob_dir):
            continue
        rel_dir = f'{plat}/{name}'
        log = subprocess.run(
            ['git', '-C', ROOT, 'log', '--oneline', '--grep', 'attempt #', '--', rel_dir],
            capture_output=True, text=True, encoding='utf-8',
        )
        if not log.stdout.strip():
            targets.append((name, prob_dir))

    if not targets:
        print(f'{plat}: 미제출 문제 없음')
        return

    print(f'{plat}: 미제출 문제 {len(targets)}개')
    for name, _ in targets:
        print(f'  - {plat}/{name}')

    answer = input('\n삭제하시겠습니까? (y/N): ').strip().lower()
    if answer != 'y':
        print('취소됨')
        return

    for name, prob_dir in targets:
        shutil.rmtree(prob_dir)
        print(f'삭제됨: {plat}/{name}')

    print(f'\n{len(targets)}개 폴더 삭제 완료')


# ── 진입점 ────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(prog='pscpp', description='BOJ 풀이 워크스페이스 CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('setup', help='초기 환경 설정 (.env 생성 + git hooks 등록)')

    for name, help_text in [
        ('new',   '문제 폴더 생성'),
        ('build', '컴파일'),
        ('test',  '예제 입출력 테스트'),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument('platform', help='플랫폼 (예: BOJ)')
        p.add_argument('prob',     help='문제 번호 (예: 1234)')

    p = sub.add_parser('submit', help='제출 직전 커밋')
    p.add_argument('platform')
    p.add_argument('prob')
    p.add_argument('message', nargs='?', default='', help='커밋 메시지 suffix')

    p = sub.add_parser('review-commit', help='AI 코드 리뷰 결과 커밋 (README.md만)')
    p.add_argument('platform')
    p.add_argument('prob')

    p = sub.add_parser('add-tc', help='테스트케이스 수동 추가')
    p.add_argument('platform')
    p.add_argument('prob')
    p.add_argument('-in', dest='tc_in', default=None, help='예제 입력 (생략 시 인터랙티브)')
    p.add_argument('-out', dest='tc_out', default=None, help='예제 출력 (생략 시 인터랙티브)')

    p = sub.add_parser('clean', help='미제출 문제 폴더 일괄 삭제')
    p.add_argument('platform', help='플랫폼 (예: BOJ)')

    args = parser.parse_args()
    env  = load_env()

    prob = getattr(args, 'prob', None)

    dispatch = {
        'setup':          lambda: cmd_setup(env),
        'new':            lambda: cmd_new(args.platform, prob),
        'build':          lambda: cmd_build(args.platform, prob, env),
        'test':           lambda: cmd_test(args.platform, prob, env),
        'submit':         lambda: cmd_submit(args.platform, prob, args.message),
        'review-commit':  lambda: cmd_review_commit(args.platform, prob),
        'add-tc':         lambda: cmd_add_tc(args.platform, prob, args.tc_in, args.tc_out),
        'clean':          lambda: cmd_clean(args.platform),
    }
    dispatch[args.command]()


if __name__ == '__main__':
    main()
