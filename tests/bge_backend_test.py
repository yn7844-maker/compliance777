import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from fastapi import HTTPException
from pydantic import ValidationError
from python_backend import server
from python_backend.prepare_documents import prepare


class BackendTests(unittest.TestCase):
    def test_authentication_and_validation(self):
        with patch.dict(os.environ, {'BGE_API_KEY': 'test-key'}):
            for auth in (None, 'Bearer wrong'):
                with self.assertRaises(HTTPException) as error:
                    server.authorize(auth)
                self.assertEqual(error.exception.status_code, 401)
            server.authorize('Bearer test-key')
            for query in [' ', 'x' * 1001]:
                with self.assertRaises(ValidationError):
                    server.Query(query=query)
            for top_k in (0, 51, 1.5):
                with self.assertRaises(ValidationError):
                    server.Query(query='x', top_k=top_k)

    def test_inference_ranking_and_missing_model(self):
        class FakeModel:
            def encode(self, *args, **kwargs):
                return np.array([1.0, 0.0])
        with patch.object(server, 'model', None):
            self.assertFalse(server.health()['ok'])
            with self.assertRaises(HTTPException) as error:
                server.search(server.Query(query='압류'))
            self.assertEqual(error.exception.status_code, 503)
        with patch.object(server, 'model', FakeModel()), patch.object(server, 'vectors', np.array([[0., 1.], [1., 0.]])), patch.object(server, 'docs', [{'id': 'A'}, {'id': 'B'}]):
            result = server.search(server.Query(query='압류', top_k=1))
            self.assertEqual(result['results'][0]['id'], 'B')
            self.assertEqual(result['results'][0]['score'], 1.)

    def test_document_import(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'guide.md').write_text('# 업무 기준\n' + '권리관계 확인. ' * 300, encoding='utf-8')
            rows = prepare(root)
            self.assertGreater(len(rows), 1)
            self.assertEqual(len({r['id'] for r in rows}), len(rows))
            self.assertTrue(all(len(r['content']) <= 1200 for r in rows))
            self.assertEqual(rows, prepare(root))


if __name__ == '__main__':
    unittest.main()
