"""Assemble release assets and public hashes; original ROM is read-only."""
import argparse,hashlib,json,re,shutil,struct,zipfile
from pathlib import Path

BASE='N64-Ganbare-Goemon-Derodero-Dochu-Obake-Tenko-Mori-Kr'
EXE_NAME='N64-Ganbare-Goemon-Derodero-Dōchū-Obake-Tenko-Mori-Kr.exe'
REPO='https://github.com/OldManCraveGuitars-bit/'+BASE
def sha(data):return hashlib.sha256(data).hexdigest()
def zip_files(path,files):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in files:
            info=zipfile.ZipInfo(name,(2026,10,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(path) as z:assert z.testzip() is None

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];dist=root/'dist';exe=dist/EXE_NAME
    assert exe.is_file(), 'Build the EXE with the exact release filename first.'
    manifest=json.loads((root/'data/manifest.json').read_text(encoding='utf8'))
    valid=json.loads((root/'docs/validation.json').read_text(encoding='utf8'))
    assert valid['passed'] and valid['exe_sha256']==sha(exe.read_bytes())
    source=a.original.read_bytes();assert sha(source)==manifest['source_sha256']
    hashes=[]
    for width,extension in [(1,'z64'),(2,'v64'),(4,'n64')]:
        raw=bytearray(len(source))
        for i in range(width):raw[i::width]=source[width-1-i::width]
        hashes.append(dict(format=extension,bytes=len(raw),header=raw[:4].hex().upper(),sha256=sha(raw),sha1=hashlib.sha1(raw).hexdigest()))
    (root/'docs/source-and-output-hashes.json').write_text(json.dumps(dict(supported_originals=hashes,
        output_format='z64',output_bytes=manifest['target_bytes'],output_sha256=manifest['target_sha256']),indent=2)+'\n',encoding='utf8')
    patch=root/'data'/manifest['patch_file'];shutil.copy2(patch,dist/patch.name)
    readme=(root/'README.md').read_text(encoding='utf8').replace('{{EXE_SHA256}}',sha(exe.read_bytes())).replace('{{BPS_SHA256}}',sha(patch.read_bytes()))
    readme=re.sub(r'(\| Windows EXE \| `)[0-9a-f]{64}(` \|)',lambda m:m[1]+sha(exe.read_bytes())+m[2],readme)
    readme=re.sub(r'(\| BPS 패치 \| `)[0-9a-f]{64}(` \|)',lambda m:m[1]+sha(patch.read_bytes())+m[2],readme)
    (root/'README.md').write_text(readme,encoding='utf8')
    howto=('힘내라! 고에몽 — 비공식 한글화 v1.0 정식 버전\n한글화: 기타 깎는 노인\n\n'
        '1. EXE를 실행하고 일본판 원본 .z64/.v64/.n64를 선택합니다.\n'
        '2. 새 출력 경로를 고르고 한글 패치 적용을 누릅니다.\n'
        '3. 결과 SHA256 검증이 완료되면 생성된 .z64 롬을 부팅합니다.\n\n'
        '원본 16 MiB → 결과 32 MiB. 원본과 기존 출력은 덮어쓰지 않습니다.\n'
        'CountPerOp 1 · SRAM · 2인 설정을 확인하세요.\n'
        '다른 버전의 세이브스테이트 대신 게임 내 저장 데이터를 사용하세요.\n\n'
        'BPS 단독 패치는 big endian .z64 원본용입니다.\n'
        '원본 SHA256: '+manifest['source_sha256']+'\n'
        '결과 SHA256: '+manifest['target_sha256']+'\n\n'
        '게임 원본과 완성 롬은 포함하지 않습니다.\n'+REPO+'\n')
    (dist/'사용법.txt').write_text(howto,encoding='utf8')
    shutil.copy2(root/'data/emulator-settings.txt',dist/'에뮬레이터-설정.txt')
    members=[(exe.name,exe.read_bytes()),(patch.name,patch.read_bytes()),('사용법.txt',howto.encode('utf8')),
             ('에뮬레이터-설정.txt',(dist/'에뮬레이터-설정.txt').read_bytes())]
    inner=''.join(sha(data)+'  '+name+'\n'for name,data in members).encode('utf8')
    members.append(('SHA256SUMS.txt',inner))
    windows=dist/(BASE+'-v1.0-Windows.zip');zip_files(windows,members)
    screens=dist/'Screenshots-v1.0.zip';zip_files(screens,[(p.name,p.read_bytes())for p in sorted((root/'docs/screenshots').glob('*.png'))])
    assets=[exe,dist/patch.name,windows,screens]
    sums=''.join(sha(p.read_bytes())+'  '+p.name+'\n'for p in assets)
    (root/'SHA256SUMS.txt').write_text(sums,encoding='utf8');(dist/'SHA256SUMS.txt').write_text(sums,encoding='utf8')
    raw=REPO.replace('https://github.com/','https://raw.githubusercontent.com/')+'/v1.0/'
    notes=('## 비공식 한글화 v1.0 정식 버전\n\n'
        '**힘내라! 고에몽 — 오싹오싹 여행길 유령 대잔치 / Nintendo 64 일본판**\n\n'
        '**한글화: 기타 깎는 노인**\n\n'
        '일본어 대사·메뉴·간판·가사 자막을 한국어로 표시하며, 반각 띄어쓰기와 선택지·대사창 배치를 보정했습니다. '
        '로봇전 UI, 게임 오버·클리어 표시와 붓글씨 제작진 크레딧을 정리했습니다. 기존 영문 표시와 OK는 유지합니다.\n\n'
        '### 다운로드 및 사용법\n\n'
        '- Windows EXE 패처 또는 Windows ZIP을 받으세요. Python 설치 없이 실행합니다.\n'
        '- 원본 .z64/.v64/.n64를 선택하면 별도의 .z64 결과를 만듭니다. 원본과 기존 출력은 보존합니다.\n'
        '- 원본 16 MiB → 결과 32 MiB. 게임 원본·완성 롬은 배포하지 않습니다.\n'
        '- CountPerOp 1 · SRAM · 2인 설정을 확인하고, 게임 내 저장 데이터를 사용하세요.\n'
        '- BPS 단독 패치는 big endian .z64 원본에 적용합니다.\n\n'
        '### SHA256\n\n'
        '| 대상 | SHA256 |\n| --- | --- |\n'
        '| 원본 .z64 | `'+manifest['source_sha256']+'` |\n'
        '| 결과 .z64 | `'+manifest['target_sha256']+'` |\n'
        '| Windows EXE | `'+sha(exe.read_bytes())+'` |\n'
        '| BPS | `'+sha(patch.read_bytes())+'` |\n\n'
        'ZIP 등 배포 파일 전체 해시는 첨부한 **SHA256SUMS.txt**에 있습니다.\n\n'
        '### 인게임 스크린샷\n\n')
    for name in ['01-title.png','02-character-select.png','04-ending-staff.png','05-localization-credit.png']:
        notes+='![인게임 화면]('+raw+'docs/screenshots/'+name+')\n\n'
    notes+=('### 확인 및 제보\n\n'
        '배포 EXE의 실제 패치 실행을 세 가지 바이트 순서로 검사했고, 같은 결과 SHA256과 원본 보존을 확인했습니다. '
        '대사 4,991구간·반각 공백 28,915개·제작진 카드 30장의 데이터 검사와 최신 롬의 부팅·주요 화면·크레딧 캡처를 확인했습니다. '
        '엔딩 캡처는 장면 진입·진행을 앞당긴 검수용 재생이며 모든 플레이 분기의 전수 완주를 뜻하지 않습니다.\n\n'
        '작고 판독이 어려운 일부 배경 표시·장식은 원문을 유지했습니다. '
        '누락이나 배치 문제는 스크린샷과 진행 위치, 에뮬레이터/코어를 함께 [Issues]('+REPO+'/issues)에 알려 주세요.\n')
    (root/'docs/RELEASE-v1.0.md').write_text(notes,encoding='utf8')
    report=dict(passed=True,version='1.0',release_name='비공식 한글화 v1.0 정식 버전',
        repo=REPO,game_ROM_files_included=False,exe_filename_preserved_in_zip=exe.name,
        assets=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in assets])
    (root/'.qa/package-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
