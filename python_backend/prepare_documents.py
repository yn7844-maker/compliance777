"""Create the search corpus from UTF-8 .txt/.md files or validated JSON arrays."""
import argparse
import hashlib
import json
from pathlib import Path
from python_backend.corpus import load_documents


def prepare(folder):
    rows = []
    for path in sorted(Path(folder).rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.txt', '.md', '.json'):
            continue
        if path.suffix.lower() == '.json':
            rows.extend(load_documents(path))
            continue
        text = path.read_text(encoding='utf-8').strip()
        if not text:
            continue
        source = path.relative_to(folder).as_posix()
        title = next((line.lstrip('#').strip() for line in text.splitlines() if line.strip()), path.stem)[:160]
        for i, start in enumerate(range(0, len(text), 1000)):
            content = text[start:start + 1200]
            digest = hashlib.sha256(f'{source}:{i}'.encode()).hexdigest()[:16]
            rows.append({'id': f'DOC-{digest}', 'kind': 'knowledge', 'title': title, 'content': content, 'source': source})
            if start + 1200 >= len(text):
                break
    if not rows:
        raise ValueError('읽을 수 있는 문서가 없습니다. UTF-8 TXT/MD 또는 문서 JSON을 넣으세요.')
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('중복 문서 ID가 있습니다.')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--overwrite', action='store_true', help='Explicitly allow replacing an existing corpus.')
    args = parser.parse_args()
    if not args.input.is_dir():
        parser.error('--input must be a directory')
    if args.output.exists() and not args.overwrite:
        parser.error('Output exists. Use --overwrite to replace it.')
    if args.output.resolve().is_relative_to(args.input.resolve()):
        parser.error('Output must be outside the input directory')
    rows = prepare(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(rows)} document chunks written to {args.output}. Restart BGE server to rebuild embeddings.')


if __name__ == '__main__':
    main()
