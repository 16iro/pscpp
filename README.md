# pscpp — BOJ / solved.ac 풀이 저장소

![CI](https://github.com/<유저명>/pscpp/actions/workflows/test.yml/badge.svg)

C++17 (GCC) · CMake 기반 알고리즘 문제 풀이 및 리뷰 저장소.

## 구조

```
pscpp/
├── BOJ/<번호>/          # 문제별 풀이 (main.cpp, README.md, 테스트)
├── templates/           # 코드 · 블로그 포스팅 템플릿
├── scripts/             # 문제 생성 · 테스트 · 커밋 자동화
└── notes/               # 알고리즘 개념 정리 · 재사용 스니펫
```

## 빠른 시작

```bash
# 새 문제 시작
./scripts/new_prob.sh BOJ 1234

# 로컬 테스트
./scripts/test.sh BOJ 1234

# 제출 직전 커밋
./scripts/submit.sh BOJ 1234 "접근 방법 요약"
```

## 진행 현황

[SOLUTIONS.md](SOLUTIONS.md) 참고.
