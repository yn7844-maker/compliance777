"""Shared JSON corpus validation, with no ML dependencies."""
import json
from pathlib import Path


def load_documents(path):
    docs = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(docs, list) or not docs:
        raise ValueError('문서 목록은 비어 있지 않은 JSON 배열이어야 합니다.')
    seen = set()
    for doc in docs:
        if not isinstance(doc, dict):
            raise ValueError('각 문서는 객체여야 합니다.')
        for key in ('id', 'title', 'content', 'source'):
            if not isinstance(doc.get(key), str) or not doc[key].strip():
                raise ValueError(f'필수 문서 필드: {key}')
        if doc['id'] in seen:
            raise ValueError('문서 ID가 중복되었습니다.')
        seen.add(doc['id'])
        for key in ('kind', 'target_type', 'result', 'rule_id'):
            if key in doc and not isinstance(doc[key], str):
                raise ValueError(f'문서 필드는 문자열이어야 합니다: {key}')
    return docs
