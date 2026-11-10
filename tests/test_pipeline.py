"""Behavioral checks for the portable pipeline, using isolated temporary output."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'paper_reading.py'
spec = importlib.util.spec_from_file_location('paper_reading', SCRIPT)
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.out = self.root / 'study'
        self.pdf = self.root / 'paper.pdf'
        # init's optional parser is mocked; hash validation still uses actual bytes.
        self.pdf.write_bytes(b'%PDF-1.4\n% isolated test fixture\n%%EOF')
        with patch.object(rp, 'pdf_info', return_value=(2, 'fixture', [])):
            self.assertEqual(rp.main(['init', '--paper', str(self.pdf), '--out', str(self.out), '--title', 'Test <paper>']), 0)

    def tearDown(self):
        self.tmp.cleanup()

    def content(self):
        return {'schema_version': 1, 'status': 'complete', 'title': 'A < B', 'summary': 'A test of rendering.',
                'sections': [{'heading': 'Evidence', 'blocks': [
                    {'type': 'paragraph', 'text': '<script>alert("x")</script>', 'pages': [1]},
                    {'type': 'paragraph_guide', 'id': 'P1', 'original': 'Original text.', 'note': 'Explanation.', 'pages': [2],
                     'blocks': [{'type': 'details', 'summary': 'Recall', 'blocks': [{'type': 'paragraph', 'text': 'Answer.'}]}]}
                ]}]}

    def fill(self):
        for folder, _, _ in rp.MODULES:
            rp.write_json(self.out / folder / 'content.json', self.content())

    def test_full_render_escape_and_source_links(self):
        self.fill()
        self.assertEqual(rp.main(['validate', '--out', str(self.out)]), 0)
        self.assertEqual(rp.main(['render', '--out', str(self.out)]), 0)
        report = (self.out / rp.MODULES[0][0] / '学习报告.html').read_text()
        self.assertIn('&lt;script&gt;', report)
        self.assertNotIn('<script>', report)
        self.assertIn('source.pdf#page=2', report)
        self.assertIn('id="P1"', report)
        self.assertIn('<details>', report)
        self.assertIn('8 / 8', (self.out / '开始阅读.html').read_text())

    def test_legacy_cli_renders_and_preserves_error_exit_code(self):
        self.fill()
        legacy = SCRIPT.with_name('reading_papers.py')
        result = subprocess.run([sys.executable, str(legacy), 'render', '--out', str(self.out)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('8 / 8', (self.out / '开始阅读.html').read_text())
        (self.out / '00_原文与索引/source.pdf').write_bytes(b'changed')
        result = subprocess.run([sys.executable, str(legacy), 'validate', '--out', str(self.out)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_missing_module_and_stale_page_do_not_look_complete(self):
        self.fill()
        rp.main(['render', '--out', str(self.out)])
        missing = self.out / rp.MODULES[-1][0]
        (missing / 'content.json').unlink()
        self.assertEqual(rp.main(['validate', '--out', str(self.out)]), 1)
        self.assertEqual(rp.main(['render', '--out', str(self.out)]), 0)
        self.assertIn('这个模块尚未完成', (missing / '学习报告.html').read_text())
        self.assertIn('7 / 8', (self.out / '开始阅读.html').read_text())

    def test_selected_modules_pass_without_claiming_package_complete(self):
        story = self.out / rp.MODULES[-1][0] / 'content.json'
        rp.write_json(story, self.content())
        self.assertEqual(rp.main(['validate', '--out', str(self.out), '--modules', '08']), 0)
        result = rp.read_json(self.out / '00_原文与索引/validation_selected_report.json')
        self.assertTrue(result['passed'])
        self.assertEqual(result['validation_scope'], 'selected_modules')
        self.assertFalse(result['package_complete'])
        self.assertEqual(list(result['modules']), [rp.MODULES[-1][0]])
        self.assertEqual(rp.main(['validate', '--out', str(self.out), '--modules', '02', '08']), 1)
        self.assertEqual(rp.main(['validate', '--out', str(self.out)]), 1)
        self.assertTrue((self.out / '00_原文与索引/validation_selected_report.json').exists())
        self.assertEqual(rp.main(['validate', '--out', str(self.out), '--modules', '09']), 2)

    def test_path_traversal_and_symlink_rejected(self):
        module = self.out / rp.MODULES[0][0]
        outside = self.root / 'outside.png'
        outside.write_bytes(b'not an image')
        (module / 'escape.png').symlink_to(outside)
        for path in ['../outside.png', str(outside), 'https://example.org/x.png', 'escape.png', 'C:\\x.png']:
            c = self.content()
            c['sections'][0]['blocks'].append({'type': 'image', 'src': path, 'alt': 'diagram'})
            with self.subTest(path=path), self.assertRaises(rp.InputError):
                rp.validate_content(c, module, 2)

    def test_page_bounds_duplicate_ids_placeholder_and_hash(self):
        module = self.out / rp.MODULES[0][0]
        for mutation in ('pages', 'ids', 'placeholder'):
            c = self.content()
            if mutation == 'pages':
                c['sections'][0]['blocks'][0]['pages'] = [3]
            elif mutation == 'ids':
                c['sections'][0]['blocks'].append(c['sections'][0]['blocks'][1])
            else:
                c['sections'][0]['blocks'][0]['text'] = 'TODO'
            with self.subTest(mutation=mutation), self.assertRaises(rp.InputError):
                rp.validate_content(c, module, 2)
        (self.out / '00_原文与索引/source.pdf').write_bytes(b'changed')
        self.assertEqual(rp.main(['validate', '--out', str(self.out)]), 2)

if __name__ == '__main__':
    unittest.main()
