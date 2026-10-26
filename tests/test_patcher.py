"""Release checks against a separately supplied original ROM."""
import hashlib,json,os,shutil,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patcher_core import normalize,patch_file,load_bundle,SOURCE_SHA256,TARGET_SHA256
from bps import apply

ROOT=Path(__file__).resolve().parents[1]
class PatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name=os.environ.get('GOEMON_TEST_ROM')
        if not name:raise unittest.SkipTest('Set GOEMON_TEST_ROM to a separately supplied Japanese original ROM.')
        cls.original=Path(name).resolve();cls.raw=cls.original.read_bytes();cls.source=normalize(cls.raw)
        assert hashlib.sha256(cls.source).hexdigest()==SOURCE_SHA256
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='goemon-patcher-');self.folder=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_three_byte_orders(self):
        for width in [1,2,4]:
            with self.subTest(width=width):
                raw=bytearray(len(self.source))
                for i in range(width):raw[i::width]=self.source[width-1-i::width]
                original=self.folder/f'일본판 원본 {width}.rom';original.write_bytes(raw)
                out=self.folder/f'한글 결과 {width}.z64';result=patch_file(original,out,ROOT/'data')
                self.assertEqual(result['target_sha256'],TARGET_SHA256)
                self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(),TARGET_SHA256)
                self.assertEqual(original.read_bytes(),raw)
    def test_wrong_original_rejected(self):
        data=bytearray(self.source);data[-1]^=1;p=self.folder/'wrong.z64';p.write_bytes(data)
        with self.assertRaisesRegex(ValueError,'해시가 다릅니다'):patch_file(p,self.folder/'out.z64',ROOT/'data')
        self.assertFalse((self.folder/'out.z64').exists())
    def test_wrong_size_rejected(self):
        p=self.folder/'short.n64';p.write_bytes(self.source[:512])
        with self.assertRaisesRegex(ValueError,'16 MiB'):patch_file(p,self.folder/'out.z64',ROOT/'data')
    def test_original_existing_output_and_hardlink_protected(self):
        with self.assertRaisesRegex(ValueError,'원본 롬'):patch_file(self.original,self.original,ROOT/'data')
        out=self.folder/'keep.z64';out.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):patch_file(self.original,out,ROOT/'data')
        self.assertEqual(out.read_bytes(),b'preserve')
        link=self.folder/'same-file.z64'
        try:os.link(self.original,link)
        except OSError:pass
        else:
            with self.assertRaisesRegex(ValueError,'원본 롬'):patch_file(self.original,link,ROOT/'data')
        self.assertEqual(self.original.read_bytes(),self.raw)
    def test_corrupt_patch_and_wrong_bundle_rejected(self):
        bundle=self.folder/'data';shutil.copytree(ROOT/'data',bundle)
        manifest=json.loads((bundle/'manifest.json').read_text(encoding='utf8'));p=bundle/manifest['patch_file']
        data=bytearray(p.read_bytes());data[-1]^=1;p.write_bytes(data)
        with self.assertRaisesRegex(ValueError,'내장 패치'):patch_file(self.original,self.folder/'out.z64',bundle)
        manifest['version']='0.0';(bundle/'manifest.json').write_text(json.dumps(manifest),encoding='utf8')
        with self.assertRaisesRegex(ValueError,'버전'):load_bundle(bundle)
    def test_bps_crc_checks(self):
        patch,_=load_bundle(ROOT/'data')
        data=bytearray(patch);data[len(data)//2]^=1
        with self.assertRaisesRegex(ValueError,'손상'):apply(self.source,data)
        source=bytearray(self.source);source[100]^=1
        with self.assertRaisesRegex(ValueError,'원본 롬 CRC'):apply(source,patch)

if __name__=='__main__':unittest.main()
