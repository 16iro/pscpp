# pscpp — BOJ / solved.ac 풀이 저장소

![CI](https://github.com/16iro/pscpp/actions/workflows/test.yml/badge.svg)

C++17 · CMake 기반 알고리즘 문제 풀이 및 리뷰 저장소.

## 구조

```
pscpp/
├── BOJ/<번호>/          # 문제별 풀이
│   ├── main.cpp         # 풀이 코드
│   ├── README.md        # 리뷰 · 블로그 포스팅용
│   ├── info.json        # 문제 메타데이터 (티어, 태그, 제한, 문제 원문)
│   └── tc/              # 테스트케이스
│       ├── 1.in / 1.out
│       └── 2.in / 2.out
├── bits/
│   └── stdc++.h         # MSVC 호환 스텁 (GCC는 자체 제공)
├── templates/           # 코드 · 블로그 포스팅 · 스킬 프롬프트 템플릿
│   └── skills/          # AI 스킬 공유 프롬프트 원본 (hint, code-review)
├── extension/           # 브라우저 익스텐션 (BOJ 문제 폴더 자동 생성)
├── native-host/         # 익스텐션 ↔ 로컬 파일시스템 브릿지
└── notes/               # 알고리즘 개념 정리 · 재사용 스니펫
```

---

## 환경 설정

클론 후 setup 스크립트를 **한 번만** 실행하면 `.env` 자동 생성 + git hook 등록 + AI 스킬 빌드까지 완료된다.

```powershell
# Windows
.\setup.bat
```
```bash
# macOS / Linux
./setup.sh
```

이후 `git clone` / `checkout` 시 `.env` 가 없으면 hook이 자동으로 재생성한다.  
경로가 다르다면 생성된 `.env` 를 직접 수정.

```dotenv
MSYS2_ROOT=C:\msys64   # MSYS2 설치 경로
COMPILER=gcc           # gcc (MSYS2/GCC) | msvc (Visual Studio)
```

```dotenv
MSYS2_ROOT=C:\msys64   # MSYS2 설치 경로
COMPILER=gcc           # gcc (MSYS2/GCC) | msvc (Visual Studio)
```

| `COMPILER` | 사용 툴체인 | cmake 제너레이터 |
|------------|------------|----------------|
| `gcc`      | MSYS2 MinGW-w64 | MinGW Makefiles |
| `msvc`     | Visual Studio (cl.exe) | 기본값 (VS) |

> **MSVC + `bits/stdc++.h`**: CMakeLists.txt 가 MSVC 빌드 시 자동으로 `bits/` 를 include path 에 추가하므로 코드 변경 없이 사용 가능.

---

## 빠른 시작 (CLI)

Windows / macOS / Linux 동일한 명령어 사용.

```bash
python pscpp.py setup                                       # 초기 설정 (.env + hooks + 스킬 빌드)
python pscpp.py new            BOJ 1234                     # 문제 폴더 생성
python pscpp.py build          BOJ 1234                     # 컴파일
python pscpp.py test           BOJ 1234                     # 예제 입출력 자동 검증
python pscpp.py save           BOJ 1234                     # 풀이 중간 저장 (WIP 커밋)
python pscpp.py save           BOJ 1234 "BFS 구현중"         # WIP + 메모
python pscpp.py submit         BOJ 1234 "접근 방법"          # 제출 직전 커밋 (attempt #N)
python pscpp.py add-tc         BOJ 1234                     # 테스트케이스 추가 (인터랙티브)
python pscpp.py add-tc         BOJ 1234 -in "1 2" -out "3"  # 테스트케이스 추가 (원라이너)
python pscpp.py review-commit  BOJ 1234                     # AI 코드 리뷰 결과 커밋
python pscpp.py clean          BOJ                          # 미제출 문제 폴더 일괄 삭제

# AI 스킬 (Claude Code / Gemini CLI)
/hint         BOJ 11724 progress                             # 진행도 힌트
/hint         BOJ 11724 errline                              # 오류 라인 힌트
/hint         BOJ 11724 errfunc                              # 오류 함수 힌트
/hint         BOJ 11724 counter                              # 반례 제공
/code-review  BOJ 11724                                      # 코드 리뷰 + README 첨삭
```

### 예제 파일 형식

테스트케이스는 문제 폴더 하위 `tc/` 디렉토리에 개별 파일로 관리:

```
BOJ/1234/tc/
├── 1.in    # 예제 입력 1
├── 1.out   # 예제 출력 1
├── 2.in    # 예제 입력 2
└── 2.out   # 예제 출력 2
```

브라우저 익스텐션이 자동 생성하며, `add-tc` 커맨드로 수동 추가도 가능.

### 테스트케이스 수동 추가

```bash
# 인터랙티브 모드 — 복사 붙여넣기에 최적
python pscpp.py add-tc BOJ 1234
[예제 입력] (빈 줄로 종료):
5
2 4 -10 4 -9

[예제 출력] (빈 줄로 종료):
2 1 4 5 1

# 원라이너 — \n 이스케이프 지원
python pscpp.py add-tc BOJ 1234 -in "5\n2 4 -10 4 -9" -out "2 1 4 5 1"
```

---

## 브라우저 익스텐션

BOJ 문제 페이지에서 클릭 한 번으로 풀이 폴더를 자동 생성.  
[Native Messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging) 기반으로 로컬 파일시스템과 통신.

### 설치

**1. 네이티브 호스트 등록**

```powershell
# Firefox (Windows)
native-host\install.bat --browser firefox

# Chrome (Windows) — 익스텐션 ID 필요, 아래 2단계 후 재실행
native-host\install.bat --browser chrome --extension-id <ID>
```

```bash
# Firefox (macOS / Linux)
./native-host/install.sh --browser firefox
```

**2. 익스텐션 로드**

| 브라우저 | 방법 |
|---------|------|
| Firefox | `about:debugging` → 이 Firefox → 임시 부가 기능 로드 → `extension/manifest.json` |
| Chrome  | `chrome://extensions` → 개발자 모드 → 압축 해제된 확장 프로그램 로드 → `extension/` |

Chrome은 표시된 Extension ID를 복사 후 네이티브 호스트 재등록 필요.

### 사용

1. `acmicpc.net/problem/<번호>` 접속
2. 툴바의 **pscpp helper** 클릭
3. 문제 정보(티어 · 태그 · 예제 수) 확인
4. **폴더 생성** 클릭 → `BOJ/<번호>/` 자동 생성, 예제 입출력 자동 입력
5. 폴더가 이미 있으면 예제만 갱신 / **초기화 토글** ON 시 전체 재생성

> Firefox는 임시 로드이므로 재시작 시 재등록 필요.  
> 영구 설치: [web-ext](https://extensionworkshop.com/documentation/develop/getting-started-with-web-ext/) 참고.

---

## AI 스킬 (hint / code-review)

`templates/skills/`에 공유 프롬프트 원본을 관리하며, `setup` 시 LLM별 스킬 파일을 자동 생성한다.

| LLM | 생성 위치 | 비고 |
|-----|----------|------|
| Claude Code | `.claude/skills/*/SKILL.md` | 프론트매터 포함 |
| Gemini CLI | `.gemini/instructions/*.md` | 본문만 |

```bash
# 스킬 프롬프트 수정 후 재빌드
python pscpp.py setup
```

생성된 스킬 파일은 `.gitignore`로 추적 제외. 새 LLM 추가 시 `pscpp.py`의 `SKILL_FRONTMATTER` / `SKILL_TARGETS`에 항목 추가.

---

## 커밋 전략

`submit.bat` 은 제출 직전 스냅샷을 자동 커밋:

```
BOJ/1234: attempt #1 - brute force O(n^2)
BOJ/1234: attempt #2 - optimize with BIT O(n log n)  ← AC
```

attempt 번호는 해당 문제 폴더의 커밋 수에서 자동 계산.

---

## CI (GitHub Actions)

`BOJ/*/main.cpp` 변경 push 시 변경된 문제만 빌드 + 예제 diff 자동 검증.  
결과는 상단 배지 또는 Actions 탭에서 확인.

---

## 진행 현황

[SOLUTIONS.md](SOLUTIONS.md) 참고.
