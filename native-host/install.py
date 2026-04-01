#!/usr/bin/env python3
"""
pscpp Native Host 설치 스크립트

사용법:
  python install.py --browser firefox
  python install.py --browser chrome --extension-id <ID>

지원 조합:
  브라우저 : firefox | chrome
  OS       : windows | macos | linux  (자동 감지)
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

HOST_NAME = 'com.pscpp.host'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Browser Adapters ──────────────────────────────────────────

class BrowserAdapter:
    name: str

    def host_manifest(self, host_path: str, ext_id: str | None) -> dict:
        raise NotImplementedError

    def registry_key(self) -> str:          # Windows only
        raise NotImplementedError

    def install_dir(self, os_type: str) -> str:
        raise NotImplementedError


class FirefoxAdapter(BrowserAdapter):
    name = 'firefox'

    def host_manifest(self, host_path, ext_id=None):
        # Firefox는 gecko ID 사용 → extension_id 불필요
        return {
            'name': HOST_NAME,
            'description': 'pscpp 문제 폴더 생성 호스트',
            'path': host_path,
            'type': 'stdio',
            'allowed_extensions': ['pscpp@helper'],
        }

    def registry_key(self):
        return r'Software\Mozilla\NativeMessagingHosts\com.pscpp.host'

    def install_dir(self, os_type):
        home = os.path.expanduser('~')
        return {
            'windows': None,   # Windows는 레지스트리 사용
            'macos':   os.path.join(home, 'Library', 'Application Support',
                                   'Mozilla', 'NativeMessagingHosts'),
            'linux':   os.path.join(home, '.mozilla', 'native-messaging-hosts'),
        }[os_type]


class ChromeAdapter(BrowserAdapter):
    name = 'chrome'

    def host_manifest(self, host_path, ext_id=None):
        if not ext_id:
            raise ValueError('Chrome은 --extension-id 가 필요합니다.')
        return {
            'name': HOST_NAME,
            'description': 'pscpp 문제 폴더 생성 호스트',
            'path': host_path,
            'type': 'stdio',
            'allowed_origins': [f'chrome-extension://{ext_id}/'],
        }

    def registry_key(self):
        return r'Software\Google\Chrome\NativeMessagingHosts\com.pscpp.host'

    def install_dir(self, os_type):
        home = os.path.expanduser('~')
        return {
            'windows': None,
            'macos':   os.path.join(home, 'Library', 'Application Support',
                                   'Google', 'Chrome', 'NativeMessagingHosts'),
            'linux':   os.path.join(home, '.config', 'google-chrome',
                                   'NativeMessagingHosts'),
        }[os_type]


BROWSER_ADAPTERS: dict[str, BrowserAdapter] = {
    'firefox': FirefoxAdapter(),
    'chrome':  ChromeAdapter(),
}


# ── OS Adapters ───────────────────────────────────────────────

def detect_os() -> str:
    s = platform.system()
    return {'Windows': 'windows', 'Darwin': 'macos'}.get(s, 'linux')


def host_executable(os_type: str) -> str:
    """네이티브 호스트 실행 파일 경로. Windows는 .bat 래퍼를 가리킨다."""
    if os_type == 'windows':
        return os.path.join(SCRIPT_DIR, 'pscpp_host.bat')
    return os.path.join(SCRIPT_DIR, 'pscpp_host.py')


def install_windows(manifest: dict, reg_key: str, json_path: str):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    subprocess.run(
        ['reg', 'add', f'HKCU\\{reg_key}',
         '/ve', '/t', 'REG_SZ', '/d', json_path, '/f'],
        check=True,
    )
    print(f'레지스트리 등록 완료: HKCU\\{reg_key}')


def install_unix(manifest: dict, install_dir: str, json_path: str):
    os.makedirs(install_dir, exist_ok=True)
    dest = os.path.join(install_dir, f'{HOST_NAME}.json')

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    shutil.copy(json_path, dest)

    # 호스트 스크립트 실행 권한
    py_path = os.path.join(SCRIPT_DIR, 'pscpp_host.py')
    os.chmod(py_path, 0o755)

    print(f'설치 완료: {dest}')


# ── 진입점 ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='pscpp native host 설치')
    parser.add_argument('--browser', required=True, choices=BROWSER_ADAPTERS.keys())
    parser.add_argument('--extension-id', default=None,
                        help='Chrome 전용: 익스텐션 ID')
    args = parser.parse_args()

    os_type = detect_os()
    adapter = BROWSER_ADAPTERS[args.browser]
    host_path = host_executable(os_type)
    json_path = os.path.join(SCRIPT_DIR, f'{HOST_NAME}.json')

    print(f'브라우저 : {adapter.name}')
    print(f'OS       : {os_type}')
    print(f'호스트   : {host_path}')

    manifest = adapter.host_manifest(host_path, args.extension_id)

    if os_type == 'windows':
        install_windows(manifest, adapter.registry_key(), json_path)
    else:
        install_dir = adapter.install_dir(os_type)
        install_unix(manifest, install_dir, json_path)

    print('브라우저를 재시작하면 호스트가 활성화됩니다.')


if __name__ == '__main__':
    main()
