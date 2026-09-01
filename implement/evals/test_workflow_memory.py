import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
IMPLEMENT = ROOT / "implement"


class ImplementWorkflowMemoryEvalTest(unittest.TestCase):
    def setUp(self):
        self.skill = (IMPLEMENT / "SKILL.md").read_text()
        self.evals = json.loads((IMPLEMENT / "evals/evals.json").read_text())

    def test_adapter_uses_active_injected_protocol(self):
        self.assertEqual((IMPLEMENT / "references/.shared").read_text().splitlines()[-1], "memory")
        self.assertIn("references/memory/workflow-memory.md", self.skill)
        self.assertIn("Workflow memory lifecycle (automatic)", self.skill)
        self.assertNotIn("evaluation-only", self.skill)

    def test_public_dispatch_scenarios_cover_hard_guards(self):
        names = {case["name"] for case in self.evals["evals"]}
        self.assertEqual(
            names,
            {
                "memory-issue-first-worker-isolation",
                "memory-nested-pair-session",
                "memory-persisted-capture-and-correction",
                "memory-fail-open-warning-and-frontier",
                "memory-standalone-close-boundaries",
                "memory-release-active",
            },
        )
        enabled = self.evals["evals"][:-1]
        self.assertTrue(all("fake version-one" in case["prompt"] for case in enabled))
        self.assertTrue(all(case["assertions"] for case in self.evals["evals"]))

    def test_fresh_worker_authority_is_explicit(self):
        self.assertIn("first load the current user instruction", self.skill)
        self.assertIn("Only then open one quiet outer session", self.skill)
        self.assertIn("issue and repository data only", self.skill)
        self.assertRegex(self.skill, r"Never copy or paraphrase\s+recalled task intent")
        for authority in (
            "scope",
            "acceptance criteria",
            "dependencies",
            "architecture decisions",
            "human approval",
            "task state",
            "frontier",
        ):
            self.assertIn(authority, self.skill)

    def test_capture_and_lifecycle_are_implement_owned(self):
        self.assertIn("persisted a human gate", self.skill)
        self.assertIn("passed its behavior proof and every required guard", self.skill)
        self.assertIn("Do not capture speculative worker output", self.skill)
        self.assertIn("does not recall,\nflush, or start another warning budget", self.skill)
        self.assertIn("normal completion,\nexplicit pause or stop, and handoff", self.skill)

    def test_adapter_has_no_direct_memory_dependencies(self):
        for forbidden in ("SQLite", "FastEmbed", "outbox", "client configuration", "daemon"):
            self.assertNotIn(forbidden, self.skill)


if __name__ == "__main__":
    unittest.main()
