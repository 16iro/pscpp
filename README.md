# pscpp — BOJ / solved.ac 풀이 저장소

![CI](https://github.com/16iro/pscpp/actions/workflows/test.yml/badge.svg)

C++17 (GCC) · CMake 기반 알고리즘 문제 풀이 및 리뷰 저장소.

## 구조

```
pscpp/
├── BOJ/<번호>/          # 문제별 풀이 (main.cpp, README.md, 테스트)
├── templates/           # 코드 · 블로그 포스팅 템플릿
├── scripts/             # 문제 생성 · 테스트 · 커밋 자동화
├── extension/           # 브라우저 익스텐션 (BOJ 문제 폴더 자동 생성)
├── native-host/         # 익스텐션 ↔ 로컬 파일시스템 브릿지
└── notes/               # 알고리즘 개념 정리 · 재사용 스니펫
```

## 브라우저 익스텐션 설치

BOJ 문제 페이지에서 클릭 한 번으로 풀이 폴더를 자동 생성한다.  
내부적으로 [Native Messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging)을 사용하므로 **네이티브 호스트 등록**이 필요하다.

### 1. 네이티브 호스트 등록

```bash
# Firefox (Windows)
native-host\install.bat --browser firefox

# Firefox (macOS / Linux)
./native-host/install.sh --browser firefox

# Chrome (Windows) — 익스텐션 ID 필요, 아래 2단계 참고
native-host\install.bat --browser chrome --extension-id <ID>
```

### 2. 익스텐션 로드

**Firefox**
1. `about:debugging` → **이 Firefox** → **임시 부가 기능 로드**
2. `extension/manifest.json` 선택

**Chrome / Chromium**
1. `chrome://extensions` → **개발자 모드** 활성화 → **압축 해제된 확장 프로그램 로드**
2. `extension/` 폴더 선택
3. 표시된 **Extension ID** 복사 후 네이티브 호스트 재등록

```bash
native-host\install.bat --browser chrome --extension-id <복사한_ID>
```

### 3. 사용

1. BOJ 문제 페이지(`acmicpc.net/problem/번호`) 접속
2. 툴바의 **pscpp helper** 아이콘 클릭
3. 문제 정보(티어 · 태그) 확인 후 **폴더 생성** 클릭
4. `BOJ/<번호>/` 폴더와 `main.cpp` · `README.md` · `input.txt` · `expected.txt` 자동 생성

> **주의**: Firefox는 임시 로드이므로 재시작 시 재등록 필요.  
> 영구 설치는 [Firefox Add-on 서명](https://extensionworkshop.com/documentation/publish/) 또는 [web-ext](https://extensionworkshop.com/documentation/develop/getting-started-with-web-ext/) 사용.

---

## 빠른 시작 (CLI)

```bash
# 새 문제 시작 (익스텐션 없이 수동으로)
./scripts/new_prob.sh BOJ 1234

# 로컬 테스트
./scripts/test.sh BOJ 1234

# 제출 직전 커밋
./scripts/submit.sh BOJ 1234 "접근 방법 요약"
```

## 진행 현황

[SOLUTIONS.md](SOLUTIONS.md) 참고.
