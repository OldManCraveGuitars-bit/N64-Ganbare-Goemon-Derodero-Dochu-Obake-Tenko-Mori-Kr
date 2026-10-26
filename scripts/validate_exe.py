"""Run the shipped Windows EXE on all three native N64 byte orders."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patcher_core import normalize,SOURCE_SHA256,TARGET_SHA256,VERSION

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];exe=root/'dist/N64-Ganbare-Goemon-Derodero-Dōchū-Obake-Tenko-Mori-Kr.exe'
    source=normalize(a.original.read_bytes());assert hashlib.sha256(source).hexdigest()==SOURCE_SHA256
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0);checks=[]
    with tempfile.TemporaryDirectory(dir=root/'.qa',prefix='패처 실행 검사 ') as temp:
        folder=Path(temp)
        def run(label,args,success):
            report=folder/(label+'.json')
            result=subprocess.run([str(exe),*map(str,args),'--report',str(report)],creationflags=flags,capture_output=True)
            assert result.returncode==(0 if success else 1),(label,result.returncode,result.stderr.decode(errors='replace'))
            info=json.loads(report.read_text(encoding='utf8'));assert info['success']==success
            return info
        info=run('embedded',['--self-test'],True);checks.append(dict(case='embedded BPS integrity',passed=True,patch_sha256=info['embedded_patch_sha256']))
        info=run('gui',['--gui-self-check'],True);assert info['gui_created'] and info['image_loaded'];checks.append(dict(case='GUI initialization and title resource',passed=True))
        for width,extension in [(1,'z64'),(2,'v64'),(4,'n64')]:
            raw=bytearray(len(source))
            for i in range(width):raw[i::width]=source[width-1-i::width]
            original=folder/('일본판 원본.'+extension);original.write_bytes(raw);output=folder/('한글 결과 '+extension+'.z64')
            info=run(extension,['--apply',original,'--output',output],True)
            assert hashlib.sha256(output.read_bytes()).hexdigest()==TARGET_SHA256
            assert original.read_bytes()==raw
            checks.append(dict(case='compiled EXE '+extension,passed=True,original_preserved=True,source_sha256=hashlib.sha256(raw).hexdigest(),output_sha256=TARGET_SHA256,output_bytes=output.stat().st_size))
            output.unlink();original.unlink()
        original=folder/'정상 원본.z64';original.write_bytes(source)
        info=run('overwrite-source',['--apply',original,'--output',original],False);assert original.read_bytes()==source
        checks.append(dict(case='original overwrite rejected',passed=True))
        output=folder/'기존 파일.z64';output.write_bytes(b'preserve')
        run('existing-output',['--apply',original,'--output',output],False);assert output.read_bytes()==b'preserve'
        checks.append(dict(case='existing output preserved',passed=True))
        bad=folder/'다른 원본.z64';data=bytearray(source);data[-1]^=1;bad.write_bytes(data)
        output=folder/'생성되면 안됨.z64';run('wrong-source',['--apply',bad,'--output',output],False);assert not output.exists()
        checks.append(dict(case='wrong source hash rejected without output',passed=True))
    report=dict(passed=True,version=VERSION,exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
        source_normalized_sha256=SOURCE_SHA256,target_sha256=TARGET_SHA256,
        compiled_executable_actually_executed=True,python_or_external_patcher_required_by_user=False,checks=checks)
    (root/'docs/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Compiled EXE passed',len(checks),'checks; all byte orders produce',TARGET_SHA256)

if __name__=='__main__':main()
