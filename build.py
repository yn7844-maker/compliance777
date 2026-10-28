from pathlib import Path
import json,shutil,subprocess
root=Path(__file__).resolve().parent
for p in (root/'data').glob('*.json'): json.loads(p.read_text(encoding='utf-8'))
for p in (root/'js').glob('*.js'): subprocess.run(['node','--check',str(p)],check=True)
out=root/'dist';out.mkdir(exist_ok=True)
shutil.copy2(root/'index.html',out/'index.html')
for name in ['css','js','data']: shutil.copytree(root/name,out/name,dirs_exist_ok=True)
print('Build OK: dist/ (no runtime dependencies, no CDN)')
