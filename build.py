from pathlib import Path
import json,shutil,subprocess
from versioning import app_version
root=Path(__file__).resolve().parent
for p in (root/'data').glob('*.json'): json.loads(p.read_text(encoding='utf-8'))
for p in (root/'js').glob('*.js'): subprocess.run(['node','--check',str(p)],check=True)
out=root/'dist';out.mkdir(exist_ok=True)
version=app_version(root)
(out/'index.html').write_text((root/'index.html').read_text(encoding='utf-8').replace('__APP_VERSION__',version),encoding='utf-8')
(out/'version.json').write_text(json.dumps({'version':version})+'\n',encoding='utf-8')
for name in ['css','js','data','fonts']: shutil.copytree(root/name,out/name,dirs_exist_ok=True)
print('Build OK: dist/ (no runtime dependencies, no CDN)')
