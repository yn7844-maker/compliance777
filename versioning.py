from pathlib import Path
import hashlib

def app_version(root):
    root=Path(root)
    paths=[root/'index.html']
    for name in ['css','js','data','fonts']:
        paths.extend(p for p in (root/name).rglob('*') if p.is_file())
    result=hashlib.sha256()
    for p in sorted(paths,key=lambda p:p.relative_to(root).as_posix()):
        result.update(p.relative_to(root).as_posix().encode());result.update(b'\0');result.update(p.read_bytes());result.update(b'\0')
    return result.hexdigest()
