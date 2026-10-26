## 비공식 한글화 v1.0 정식 버전

**힘내라! 고에몽 — 오싹오싹 여행길 유령 대잔치 / Nintendo 64 일본판**

**한글화: 기타 깎는 노인**

일본어 대사·메뉴·간판·가사 자막을 한국어로 표시하며, 반각 띄어쓰기와 선택지·대사창 배치를 보정했습니다. 로봇전 UI, 게임 오버·클리어 표시와 붓글씨 제작진 크레딧을 정리했습니다. 기존 영문 표시와 OK는 유지합니다.

### 다운로드 및 사용법

- Windows EXE 패처 또는 Windows ZIP을 받으세요. Python 설치 없이 실행합니다.
- 원본 .z64/.v64/.n64를 선택하면 별도의 .z64 결과를 만듭니다. 원본과 기존 출력은 보존합니다.
- 원본 16 MiB → 결과 32 MiB. 게임 원본·완성 롬은 배포하지 않습니다.
- CountPerOp 1 · SRAM · 2인 설정을 확인하고, 게임 내 저장 데이터를 사용하세요.
- BPS 단독 패치는 big endian .z64 원본에 적용합니다.

### SHA256

| 대상 | SHA256 |
| --- | --- |
| 원본 .z64 | `d42e0fcdcc11678f17cd1977f9b774981923bfca22a989d73d7989b09d25bdd8` |
| 결과 .z64 | `5205295d9e14a49219fcdb0b65965a28eaf9103eb8faefab2f6bcc00291558fb` |
| Windows EXE | `173a833956c9ad86a3c1d86e060da4d82561f492df47b4011c4e79577600ee5d` |
| BPS | `4da7695fc56bbef45f589a11b75baa271c5617fec888d2370c0e2b222050e9dd` |

ZIP 등 배포 파일 전체 해시는 첨부한 **SHA256SUMS.txt**에 있습니다.

### 인게임 스크린샷

![인게임 화면](https://raw.githubusercontent.com/OldManCraveGuitars-bit/N64-Ganbare-Goemon-Derodero-Dochu-Obake-Tenko-Mori-Kr/v1.0/docs/screenshots/01-title.png)

![인게임 화면](https://raw.githubusercontent.com/OldManCraveGuitars-bit/N64-Ganbare-Goemon-Derodero-Dochu-Obake-Tenko-Mori-Kr/v1.0/docs/screenshots/02-character-select.png)

![인게임 화면](https://raw.githubusercontent.com/OldManCraveGuitars-bit/N64-Ganbare-Goemon-Derodero-Dochu-Obake-Tenko-Mori-Kr/v1.0/docs/screenshots/04-ending-staff.png)

![인게임 화면](https://raw.githubusercontent.com/OldManCraveGuitars-bit/N64-Ganbare-Goemon-Derodero-Dochu-Obake-Tenko-Mori-Kr/v1.0/docs/screenshots/05-localization-credit.png)

### 확인 및 제보

배포 EXE의 실제 패치 실행을 세 가지 바이트 순서로 검사했고, 같은 결과 SHA256과 원본 보존을 확인했습니다. 대사 4,991구간·반각 공백 28,915개·제작진 카드 30장의 데이터 검사와 최신 롬의 부팅·주요 화면·크레딧 캡처를 확인했습니다. 엔딩 캡처는 장면 진입·진행을 앞당긴 검수용 재생이며 모든 플레이 분기의 전수 완주를 뜻하지 않습니다.

작고 판독이 어려운 일부 배경 표시·장식은 원문을 유지했습니다. 누락이나 배치 문제는 스크린샷과 진행 위치, 에뮬레이터/코어를 함께 [Issues](https://github.com/OldManCraveGuitars-bit/N64-Ganbare-Goemon-Derodero-Dochu-Obake-Tenko-Mori-Kr/issues)에 알려 주세요.
