# 기여 규칙

시안과 영상을 올릴 때 지켜 주세요. 규칙이 같아야 영상 편집과 기획서 정리가 쉬워집니다.

## 1. 파일 이름

영어 소문자, 숫자, 하이픈(`-`), 밑줄(`_`)만 씁니다. 한글과 띄어쓰기는 쓰지 않습니다.

| 구분 | 형식 | 예시 |
|---|---|---|
| 시안 이미지 | `단계-순서_화면명_v버전.png` | `03-02_tester-evidence_v2.png` |
| 단계 영상 | `단계_폴더명_v버전.mp4` | `03_group-proposal_v1.mp4` |
| 전체 영상 | `playfit-demo_v버전.mp4` | `playfit-demo_v1.mp4` |

- **단계**: 폴더 번호(01~07)
- **순서**: 그 단계 안에서 화면이 나오는 순서(01부터). 각 단계 README의 화면 순서표와 맞춥니다.
- **버전**: v1부터 시작하고, 수정할 때마다 올립니다.

## 2. 규격

| 구분 | 규격 |
|---|---|
| 시안 이미지 | PNG, 데스크톱 1920×1080 기준 |
| 단계 영상 | MP4(H.264), 1080p, 1분 안팎, **50MB 이하** |
| 전체 영상 | GitHub Releases에 업로드(저장소에 직접 넣지 않음) |

자세한 녹화 규칙은 [docs/video-guide.md](docs/video-guide.md)를 봅니다.

## 3. 버전 관리

- `screens/`와 `video/`에는 **최신 버전만** 둡니다.
- 새 버전을 올리면 이전 파일은 같은 단계의 `archive/`로 옮깁니다.

## 4. 브랜치와 PR

1. `main`에는 확정본만 둡니다. 직접 푸시하지 않습니다.
2. 단계별 브랜치를 만듭니다: `design/03-group-proposal`
3. 작업이 끝나면 PR을 열고 템플릿의 체크리스트를 채웁니다.
4. 팀원 1명 이상이 확인한 뒤 병합합니다.

```bash
git checkout main && git pull
git checkout -b design/03-group-proposal
# 시안 추가 후
git add 03_group-proposal/
git commit -m "03 집단 제시·선택 시안 v1 추가"
git push -u origin design/03-group-proposal
```

## 5. 함께 갱신할 것

- 해당 단계 README의 **화면 순서표** 상태
- 루트 [README.md](README.md)의 **진행 현황표** 상태(⬜ → 🟨 → ✅)

## 6. Git LFS

영상(`.mp4`, `.mov`)과 디자인 원본(`.fig`, `.psd`)은 Git LFS로 관리합니다. 처음 한 번만 설치합니다.

```bash
git lfs install
```

GitHub는 100MB가 넘는 파일을 받지 않고, LFS 무료 용량도 작습니다. 그래서 단계 영상은 짧게 만들고, 전체 영상은 Releases에 올립니다.
