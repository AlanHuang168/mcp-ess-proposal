#!/usr/bin/env python3
"""Open-Source Release Safety Gate（开源发布安全门禁）.

Implements the Deterministic Validator（确定性验证器） required by ADR-0002 D3.

Outcomes are exactly three, and they are never collapsed:

    PASS        exit 0   the scan ran and found nothing
    MATCH_FOUND exit 1   the scan ran and found something
    TOOL_ERROR  exit 2   the scan could not run correctly

TOOL_ERROR fails closed. A validator that cannot run is not a validator that
passed. Shell idioms such as ``command || echo clean`` are forbidden precisely
because they map a non-zero validator exit onto success; see GAP-008.

Scope is the public baseline: files git would track, honouring .gitignore.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PASS = 0
MATCH_FOUND = 1
TOOL_ERROR = 2

# Categories required by ADR-0002 D3.
CATEGORIES: dict[str, str] = {
    "secret_value": (
        r"(?:sk-[A-Za-z0-9]{16,}"
        r"|AKIA[0-9A-Z]{16}"
        r"|-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"
        r"|xox[baprs]-[A-Za-z0-9-]{10,}"
        r"|gh[pousr]_[A-Za-z0-9]{20,})"
    ),
    "credential_assignment": (
        r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|refresh[_-]?token"
        r"|password|passwd|client[_-]?secret)\b\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"
    ),
    "private_local_path": r"/(?:Users|home)/[A-Za-z0-9_.-]+/",
    "private_infrastructure": (
        r"(?i)(?:(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://"
        r"|\b(?:HGP_DATABASE_URL|DEEPSEEK_API_KEY|DASHSCOPE_API_KEY)\b)"
    ),
    "internal_identifier": r"(?i)(?:haisic|haisikeji|海思|\bhgp[-_]|hgp_ess|cordis|dsh[-_]ess)",
    "private_runtime_storage": r"(?i)\b(?:leads|mcp_audit)\.jsonl\b",
}

# Findings that are verified-benign. Each needs a reason, not just a path.
ALLOWLIST: dict[tuple[str, str], str] = {
    ("tests/test_configuration.py", "internal_identifier"): (
        "Negative test that deliberately splits forbidden names so the literals "
        "never appear as complete strings. Asserts the old private settings are absent."
    ),
    ("tools/release_safety_gate.py", "internal_identifier"): "This validator's own pattern table.",
    ("tools/release_safety_gate.py", "private_infrastructure"): "This validator's own pattern table.",
    ("tools/release_safety_gate.py", "private_local_path"): "This validator's own pattern table.",
    ("tools/release_safety_gate.py", "secret_value"): "This validator's own pattern table.",
    ("tools/release_safety_gate.py", "credential_assignment"): "This validator's own pattern table.",
    ("tools/release_safety_gate.py", "private_runtime_storage"): "This validator's own pattern table.",
}


def baseline_files(root: Path) -> list[Path]:
    """Files that would enter the public baseline, honouring .gitignore."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {result.stderr.strip()}")
    return [root / line for line in result.stdout.splitlines() if line]


def scan(root: Path) -> tuple[int, list[tuple[str, str, int, str]], list[str], list[str]]:
    findings: list[tuple[str, str, int, str]] = []
    allowlisted: list[str] = []
    unscannable: list[str] = []
    compiled = {name: re.compile(pattern) for name, pattern in CATEGORIES.items()}

    for path in baseline_files(root):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Binary content cannot be scanned by a text validator. Report it
            # rather than skipping silently: an unscanned file in the baseline is
            # an unverified file, and that is a human decision, not a pass.
            unscannable.append(path.relative_to(root).as_posix())
            continue
        except OSError as exc:
            raise RuntimeError(f"cannot read {path}: {exc}") from exc

        rel = path.relative_to(root).as_posix()
        for name, pattern in compiled.items():
            for number, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    if (rel, name) in ALLOWLIST:
                        allowlisted.append(f"{rel} [{name}]")
                        break
                    findings.append((rel, name, number, line.strip()[:120]))

    return (MATCH_FOUND if findings else PASS), findings, sorted(set(allowlisted)), sorted(unscannable)


def main() -> int:
    parser = argparse.ArgumentParser(description="Open-Source Release Safety Gate")
    parser.add_argument("--root", default=".", help="repository root to scan")
    parser.add_argument("--quiet", action="store_true", help="print only the verdict line")
    args = parser.parse_args()

    try:
        root = Path(args.root).resolve(strict=True)
        status, findings, allowlisted, unscannable = scan(root)
    except Exception as exc:  # noqa: BLE001 - any failure must fail closed
        print(f"TOOL_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("VERDICT: TOOL_ERROR (fail closed; this is NOT a pass)")
        return TOOL_ERROR

    if not args.quiet:
        for rel, name, number, excerpt in findings:
            print(f"MATCH_FOUND  {name:<24} {rel}:{number}: {excerpt}")
        for entry in allowlisted:
            print(f"allowlisted  {entry}")
        for entry in unscannable:
            print(f"UNSCANNABLE  binary file in baseline scope: {entry}")

    print(
        f"VERDICT: {'MATCH_FOUND' if findings else 'PASS'} "
        f"({len(findings)} finding(s), {len(allowlisted)} allowlisted, "
        f"{len(unscannable)} unscannable binary file(s))"
    )
    return status


if __name__ == "__main__":
    sys.exit(main())
