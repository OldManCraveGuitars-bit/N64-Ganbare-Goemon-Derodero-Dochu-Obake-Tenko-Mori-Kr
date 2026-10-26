"""Build a compact BPS using verified primary-file relocation boundaries.

Original/target ROMs are local inputs, never part of the publication folder.
Most moved files use BPS SourceCopy. Expanded zero padding uses TargetCopy.
"""
import argparse,hashlib,json,struct,sys,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bps import number,apply
from patcher_core import VERSION,SOURCE_SHA1,SOURCE_SHA256,TARGET_SHA256

def create(source,target,files):
    metadata=json.dumps(dict(title='힘내라! 고에몽',release='비공식 한글화 v1.0 정식 버전',
        author='기타 깎는 노인',source_sha256=SOURCE_SHA256,target_sha256=TARGET_SHA256),ensure_ascii=False).encode('utf8')
    patch=bytearray(b'BPS1')+number(len(source))+number(len(target))+number(len(metadata))+metadata
    pos=0;source_relative=0;target_relative=0;counts=dict(source_read=0,source_copy=0,target_read=0,target_copy=0)
    def literal(data):
        nonlocal pos
        if not data:return
        patch.extend(number(((len(data)-1)<<2)|1));patch.extend(data);pos+=len(data);counts['target_read']+=len(data)
    def copy(offset,count):
        nonlocal pos,source_relative
        if not count:return
        if offset==pos:patch.extend(number((count-1)<<2));counts['source_read']+=count
        else:
            patch.extend(number(((count-1)<<2)|2));delta=offset-source_relative
            patch.extend(number((abs(delta)<<1)|int(delta<0)));source_relative=offset+count;counts['source_copy']+=count
        pos+=count
    def aligned_diff(old_offset,new_offset,count,old_count):
        i=0
        while i<count:
            if i<old_count and source[old_offset+i]==target[new_offset+i]:
                end=i+1
                while end<min(count,old_count) and source[old_offset+end]==target[new_offset+end]:end+=1
                if end-i>=16:copy(old_offset+i,end-i);i=end;continue
            end=i+1
            while end<count:
                if end+16<=old_count and source[old_offset+end:old_offset+end+16]==target[new_offset+end:new_offset+end+16]:break
                end+=1
            literal(target[new_offset+i:new_offset+end]);i=end
    ptr=0x2A968
    first=struct.unpack_from('>I',target,ptr+4)[0]&0x7fffffff
    aligned_diff(0,0,first,first)
    for row in files:
        fid=row['id'];start,end=struct.unpack_from('>II',target,ptr+fid*4);start&=0x7fffffff;end&=0x7fffffff
        assert pos==start
        old_start=row['offset'];old_count=row['stored_size'];count=end-start
        if target[start:end]==source[old_start:old_start+old_count]:copy(old_start,count)
        else:aligned_diff(old_start,start,count,old_count)
    rest=len(target)-pos;assert not any(target[pos:])
    if rest:
        if not pos or target[pos-1]!=0:literal(b'\0');rest-=1
        if rest:
            offset=pos-1;delta=offset-target_relative
            patch.extend(number(((rest-1)<<2)|3));patch.extend(number((abs(delta)<<1)|int(delta<0)))
            pos+=rest;counts['target_copy']+=rest
    assert pos==len(target)
    patch.extend(struct.pack('<II',zlib.crc32(source),zlib.crc32(target)))
    patch.extend(struct.pack('<I',zlib.crc32(patch)))
    assert apply(source,patch)==target
    return bytes(patch),counts

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('target',type=Path);p.add_argument('file_index',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];source=a.original.read_bytes();target=a.target.read_bytes()
    assert hashlib.sha256(source).hexdigest()==SOURCE_SHA256 and hashlib.sha256(target).hexdigest()==TARGET_SHA256
    patch,counts=create(source,target,json.loads(a.file_index.read_text()))
    path=root/'data/Goemon-Derodero-Korean-v1.0.bps';path.write_bytes(patch)
    manifest=dict(version=VERSION,release_name='비공식 한글화 v1.0 정식 버전',source_sha1=SOURCE_SHA1,
        source_sha256=SOURCE_SHA256,source_bytes=len(source),target_sha256=TARGET_SHA256,target_bytes=len(target),
        patch_file=path.name,patch_sha256=hashlib.sha256(patch).hexdigest(),patch_bytes=len(patch),author='기타 깎는 노인')
    (root/'data/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (root/'.qa/bps-generation.json').write_text(json.dumps(dict(passed=True,roundtrip_exact=True,actions=counts,**manifest),ensure_ascii=False,indent=2),encoding='utf8')
    print('BPS',len(patch),'bytes; exact target verified',manifest['target_sha256'])

if __name__=='__main__':main()
