from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sources.py"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], text=True, capture_output=True)
    if ok and p.returncode != 0:
        raise AssertionError(p.stdout + p.stderr)
    if not ok and p.returncode == 0:
        raise AssertionError("expected failure")
    return p


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        ledger = td / "ledger.json"
        evidence = td / "page.txt"
        draft = td / "draft.md"
        evidence.write_text("The recreation centre includes a 25-metre indoor swimming pool and six courts.", encoding="utf-8")

        run("--ledger", ledger, "reset")
        run("--ledger", ledger, "add", "https://school.example/facilities", "--title", "Facilities")
        run("--ledger", ledger, "quote", "1", "--text", "includes a 25-metre indoor swimming pool", "--from", evidence)
        run("--ledger", ledger, "quote", "1", "--text", "includes a 50-metre Olympic pool", "--from", evidence, ok=False)

        draft.write_text("Students have access to a 25-metre indoor swimming pool.[1]\n", encoding="utf-8")
        run("--ledger", ledger, "render", "--style", "evidence", "--replace-in", draft)
        run("--ledger", ledger, "verify", draft, "--evidence")

        bad = td / "bad.md"
        bad.write_text("The campus has a rooftop observatory.[99]\n\n## Sources\n\n[99] https://fake.example\n", encoding="utf-8")
        run("--ledger", ledger, "verify", bad, "--evidence", ok=False)

    print("smoke tests passed")


if __name__ == "__main__":
    main()
