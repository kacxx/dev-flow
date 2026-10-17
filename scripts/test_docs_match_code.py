"""The decided docs and the logs must agree with the code (dev-flow audit, 2026-10-17).

- D4 in docs/proposals/status.md names the same doc-PR keywords as state.py, and
  the same stages; the status skill's table and the proposal's Shape 2 list them
  in state.py's PRECEDENCE order.
- On main, no proposal's Status line still says "Ready to merge".
- docs/path-tuning.md logs ideas from several repos, so every issue or PR
  reference carries its repo (owner/repo#N); only the end of a range may be bare
  (kacxx/aside-jot#82–#86).
"""
import glob
import importlib.util
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_DOC = os.path.join(ROOT, "docs", "proposals", "status.md")
STATE_PY = os.path.join(ROOT, "skills", "status", "scripts", "state.py")
STATUS_SKILL = os.path.join(ROOT, "skills", "status", "SKILL.md")
PATH_TUNING = os.path.join(ROOT, "docs", "path-tuning.md")

spec = importlib.util.spec_from_file_location("state", STATE_PY)
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def live(text):
    """Text outside superseded <details> blocks."""
    return re.sub(r"<details>.*?</details>", "", text, flags=re.S | re.I)


def d4():
    m = re.search(r"(?ms)^### D4:.*?(?=^### |\Z)", live(read(STATUS_DOC)))
    assert m, "no ### D4 in docs/proposals/status.md"
    return m.group(0)


def norm(stage):
    return re.sub(r"[^a-z ]", "", stage.lower()).strip()


def table_stages(text):
    """First column of a `| Stage | … |` table, in order."""
    rows = re.findall(r"(?m)^\|\s*([^|]+?)\s*\|", text)
    return [r for r in rows if r.lower() != "stage" and not set(r) <= set("-: ")]


def on_main():
    ref = os.environ.get("GITHUB_REF")
    if ref is not None:
        return ref == "refs/heads/main"
    try:
        out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return False
    return out == "main"


class D4MatchesStatePy(unittest.TestCase):
    def test_doc_pr_keywords(self):
        code = re.search(r"\(\?i\)\\b\(([A-Za-z|]+)\) #%d", read(STATE_PY))
        self.assertIsNotNone(code, "state.py's doc-PR regex not found")
        line = re.search(r"(?m)^A \*\*doc PR\*\*.*$", d4())
        self.assertIsNotNone(line, "D4 has no 'A **doc PR**' sentence")
        doc = set(re.findall(r"`(\w+) #N`", line.group(0)))
        self.assertEqual(doc, set(code.group(1).split("|")), "D4's doc-PR keywords vs state.py")

    def test_d4_stages_are_state_py_stages(self):
        self.assertEqual({norm(s) for s in table_stages(d4())}, {norm(s) for s in state.PRECEDENCE})

    def test_status_skill_table_is_in_precedence_order(self):
        text = read(STATUS_SKILL)
        m = re.search(r"(?ms)^\| Stage \| What it means \|.*?(?=^\s*$)", text)
        self.assertIsNotNone(m, "no stage table in skills/status/SKILL.md")
        self.assertEqual([norm(s) for s in table_stages(m.group(0))], [norm(s) for s in state.PRECEDENCE])

    def test_shape_precedence_order(self):
        m = re.search(r"first\*\* match in this order: ([^.]+)\.", read(STATUS_DOC))
        self.assertIsNotNone(m, "Shape 2's precedence sentence not found")
        self.assertEqual([norm(s) for s in m.group(1).split(", ")], [norm(s) for s in state.PRECEDENCE])


class Logs(unittest.TestCase):
    def test_no_ready_to_merge_status_on_main(self):
        # A doc PR's own draft says "Ready to merge" by design (proposal's template),
        # so this only holds once it's on main.
        if not on_main():
            self.skipTest("only checked on main")
        stale = [f"{os.path.relpath(p, ROOT)}: {l}" for p in glob.glob(os.path.join(ROOT, "docs", "proposals", "*.md"))
                 for l in read(p).splitlines() if l.startswith("Status:") and "Ready to merge" in l]
        self.assertEqual(stale, [], "merged proposals still say 'Ready to merge'")

    def test_path_tuning_references_name_their_repo(self):
        text = read(PATH_TUNING)
        bare = []
        for m in re.finditer(r"#\d+", text):
            before = text[:m.start()]
            if re.search(r"[\w.-]+/[\w.-]+$", before) or before.endswith("–"):
                continue
            line = text.count("\n", 0, m.start()) + 1
            bare.append(f"line {line}: {m.group(0)}")
        self.assertEqual(bare, [], "write owner/repo#N in path-tuning.md")

    def test_checks_catch_drift(self):
        self.assertTrue(re.search(r"#\d+", "see #82") and not re.search(r"[\w.-]+/[\w.-]+$", "see "))
        self.assertEqual([norm(s) for s in table_stages("| Stage | Marker |\n|---|---|\n| decided, full path | x |\n")],
                         ["decided full path"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
