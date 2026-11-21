"""Run every runnable exercise solution and test file in the handbook. Exit 1 on any failure.

Add new solutions to CHECKS as modules are written.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

CHECKS = [
    # (working directory, command)
    ("modules/02-computing-foundations/solution", ["bash", "-c", "./count_by_source.sh ../../../projects/admitflow/data/leads_sample.csv | grep -q 'TOTAL      120'"]),
    ("modules/03-programming-fundamentals/exercises/solutions", [PY, "ex01_basics.py"]),
    ("modules/03-programming-fundamentals/exercises/solutions", [PY, "ex02_collections.py"]),
    ("modules/03-programming-fundamentals/exercises/solutions", [PY, "ex03_files.py"]),
    ("modules/03-programming-fundamentals/exercises/solutions", [PY, "-m", "pytest", "-q", "-o", "addopts=", "test_ex04_followup.py"]),
    ("modules/03-programming-fundamentals/exercises/solutions", [PY, "ex05_fetch.py"]),
    ("modules/03-programming-fundamentals/break-and-fix/solution", [PY, "-m", "pytest", "-q", "-o", "addopts=", "test_clean_ad_leads.py"]),
    ("modules/04-software-engineering/exercises/solutions", [PY, "-m", "pytest", "-q", "-o", "addopts=", "test_course_service.py"]),
    ("modules/04-software-engineering/break-and-fix/solution", [PY, "-m", "pytest", "-q", "-o", "addopts=", "test_app.py"]),
    ("modules/05-databases-and-data-engineering/exercises/solutions", [PY, "check_sql_drills.py"]),
    ("modules/05-databases-and-data-engineering/exercises/solutions", [PY, "fee_loader.py"]),
    ("modules/05-databases-and-data-engineering/break-and-fix/solution", [PY, "-c",
        "import os, subprocess, sys, tempfile; db = os.path.join(tempfile.mkdtemp(), 'big.db'); "
        "subprocess.run([sys.executable, '../make_big_db.py', db], check=True); "
        "subprocess.run([sys.executable, 'fast_report.py', db], check=True)"]),
    ("modules/07-ai-and-machine-learning/exercises/solutions", [PY, "-W", "ignore", "ex01_explore.py"]),
    ("modules/07-ai-and-machine-learning/exercises/solutions", [PY, "-W", "ignore", "ex02_compare_models.py"]),
    ("modules/07-ai-and-machine-learning/exercises/solutions", [PY, "-W", "ignore", "ex03_capacity.py"]),
    ("modules/07-ai-and-machine-learning/exercises/solutions", [PY, "ex04_similarity.py"]),
    ("modules/07-ai-and-machine-learning/break-and-fix/solution", [PY, "-W", "ignore", "honest_model.py"]),
    ("modules/08-generative-ai-engineering/exercises/solutions", [PY, "-W", "ignore", "hybrid_search.py"]),
    ("modules/08-generative-ai-engineering/exercises/solutions", [PY, "tool_loop.py"]),
    ("modules/08-generative-ai-engineering/break-and-fix/solution", [PY, "check_fees.py"]),
    ("projects/admitflow", [PY, "-m", "admitflow.cli", "eval-assistant", "--min-correct", "0.85"]),
    ("modules/09-enterprise-integration/exercises/solutions", [PY, "webhook_sender.py"]),
    ("modules/09-enterprise-integration/break-and-fix/solution", [PY, "fixed_sync.py"]),
    ("modules/09-enterprise-integration/exercises/solutions", [PY, "mcp_followups_tool.py"], (3, 10)),
    ("modules/10-production-security-reliability/exercises/solutions", [PY, "retention.py"]),
    ("modules/10-production-security-reliability/exercises/solutions", [PY, "circuit_breaker.py"]),
    ("modules/10-production-security-reliability/break-and-fix/solution", [PY, "with_alert.py"]),
    ("modules/11-business-and-client-engineering/exercises/solutions", [PY, "roi_model.py"]),
    ("modules/11-business-and-client-engineering/break-and-fix/solution", [PY, "adoption_report.py"]),
    ("interview-prep/solutions", [PY, "coding_solutions.py"]),
]


def main() -> int:
    failed = []
    for folder, command, *needs in CHECKS:
        if needs and sys.version_info < needs[0]:
            print(f"[skip] {folder}: needs Python {'.'.join(map(str, needs[0]))}+")
            continue
        result = subprocess.run(command, cwd=ROOT / folder, capture_output=True, text=True)
        status = "ok " if result.returncode == 0 else "FAIL"
        print(f"[{status}] {folder}: {' '.join(Path(c).name if c == PY else c for c in command)}")
        if result.returncode != 0:
            failed.append(folder)
            print(result.stdout[-2000:], result.stderr[-2000:], sep="\n")
    skipped = sum(1 for _, _, *needs in CHECKS if needs and sys.version_info < needs[0])
    print(f"\n{len(CHECKS) - len(failed) - skipped}/{len(CHECKS) - skipped} passed" + (f", {skipped} skipped" if skipped else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
