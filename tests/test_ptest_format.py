"""
Validation tests for PTEST scenario format (AQ-012-P1).

Verifies that all PTEST-*.yml files in tests/prompt-regression/scenarios/:
1. Contain all required fields (id, title, level, context, request, expected, anti_patterns)
2. Have valid level values (L0-L4)
3. Have id matching the filename
4. Have no duplicate ids

Run:
    python -m pytest tests/test_ptest_format.py -v
"""
import re
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
SCENARIOS_DIR = WORKSPACE / "tests" / "prompt-regression" / "scenarios"

REQUIRED_FIELDS = {"id", "title", "level", "context", "request", "expected", "anti_patterns"}
VALID_LEVELS = {"L0", "L1", "L2", "L3", "L4"}


def _simple_yaml_parse(text: str) -> dict[str, str]:
    """Minimal YAML top-level key extraction (no nested parsing needed)."""
    result: dict[str, str] = {}
    for match in re.finditer(r"^([a-z_]+)\s*:", text, re.MULTILINE):
        result[match.group(1)] = ""
    # Extract scalar values for id and level
    for key in ("id", "level"):
        m = re.search(rf'^{key}\s*:\s*"?([^"\n]+)"?\s*$', text, re.MULTILINE)
        if m:
            result[key] = m.group(1).strip().strip('"')
    return result


class TestPtestFormat(unittest.TestCase):
    """Validate format of all PTEST scenario files."""

    @classmethod
    def setUpClass(cls):
        cls.ptest_files = sorted(SCENARIOS_DIR.glob("PTEST-*.yml"))
        cls.parsed: list[tuple[Path, dict[str, str]]] = []
        for f in cls.ptest_files:
            text = f.read_text(encoding="utf-8")
            cls.parsed.append((f, _simple_yaml_parse(text)))

    def test_scenarios_exist(self):
        self.assertGreater(
            len(self.ptest_files), 0,
            "At least one PTEST scenario file must exist",
        )

    def test_required_fields_present(self):
        for filepath, fields in self.parsed:
            for req in sorted(REQUIRED_FIELDS):
                self.assertIn(
                    req, fields,
                    f"{filepath.name}: missing required field '{req}'",
                )

    def test_valid_level_values(self):
        for filepath, fields in self.parsed:
            level = fields.get("level", "")
            self.assertIn(
                level, VALID_LEVELS,
                f"{filepath.name}: level '{level}' not in {VALID_LEVELS}",
            )

    def test_id_matches_filename(self):
        for filepath, fields in self.parsed:
            expected_id = filepath.stem  # e.g. PTEST-001
            actual_id = fields.get("id", "")
            self.assertEqual(
                actual_id, expected_id,
                f"{filepath.name}: id '{actual_id}' does not match filename '{expected_id}'",
            )

    def test_no_duplicate_ids(self):
        ids = [fields.get("id", "") for _, fields in self.parsed]
        seen: set[str] = set()
        duplicates: list[str] = []
        for ptest_id in ids:
            if ptest_id in seen:
                duplicates.append(ptest_id)
            seen.add(ptest_id)
        self.assertEqual(
            duplicates, [],
            f"Duplicate PTEST ids found: {duplicates}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
