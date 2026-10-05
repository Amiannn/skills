"""Offline installer checks; never touch the real HOME or cluster."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('nano4-workflow', 'qwen-sglang-mtp')


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nano4-skills-test-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def run_install(self, *args):
        return subprocess.run(
            ['bash', str(ROOT / 'install.sh'), *map(str, args)],
            env={**os.environ, 'HOME': str(self.home)},
            cwd=self.home, capture_output=True, text=True,
        )

    def assert_installed(self, dest, claude=False):
        for name in SKILLS:
            source = ROOT / 'skills' / name
            installed = dest / name
            for file in source.rglob('*'):
                relative = file.relative_to(source)
                if not file.is_file() or '__pycache__' in relative.parts:
                    continue
                if claude and relative.parts[0] == 'agents':
                    self.assertFalse((installed / relative).exists())
                else:
                    self.assertEqual(file.read_bytes(), (installed / relative).read_bytes())

    def test_codex_default(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_installed(self.home / '.agents/skills')

    def test_claude_default(self):
        result = self.run_install('--target', 'claude')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_installed(self.home / '.claude/skills', claude=True)
        self.assertIn('Claude Code', result.stdout)
        self.assertFalse((self.home / '.agents').exists())

    def test_custom_destinations(self):
        for target in ('codex', 'claude'):
            dest = self.home / f'{target} project/.skills'
            result = self.run_install('--target', target, dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assert_installed(dest, claude=target == 'claude')
        legacy = self.home / 'legacy'
        self.assertEqual(self.run_install(legacy).returncode, 0)
        self.assert_installed(legacy)

    def test_existing_second_skill_prevents_any_copy(self):
        dest = self.home / '.claude/skills'
        existing = dest / SKILLS[1]
        existing.mkdir(parents=True)
        result = self.run_install('--target', 'claude')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Refusing to overwrite', result.stderr)
        self.assertFalse((dest / SKILLS[0]).exists())
        self.assertEqual(list(existing.iterdir()), [])

    def test_reinstall_preserves_contents(self):
        self.assertEqual(self.run_install('--target', 'claude').returncode, 0)
        self.assertNotEqual(self.run_install('--target', 'claude').returncode, 0)
        self.assert_installed(self.home / '.claude/skills', claude=True)

    def test_dangling_symlink_collision(self):
        dest = self.home / '.agents/skills'
        dest.mkdir(parents=True)
        (dest / SKILLS[0]).symlink_to(self.home / 'missing')
        self.assertNotEqual(self.run_install().returncode, 0)
        self.assertFalse((dest / SKILLS[1]).exists())

    def test_invalid_arguments_and_help_do_not_install(self):
        for args in (('--target',), ('--target', 'invalid'), ('--unknown',), ('a', 'b')):
            self.assertEqual(self.run_install(*args).returncode, 2)
        self.assertEqual(self.run_install('--help').returncode, 0)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
