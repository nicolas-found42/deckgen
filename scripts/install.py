#!/usr/bin/env python3
"""Install the deckgen plugin into a host, or print a preview.

Hosts:
  claude  drive the Claude Code plugin CLI (marketplace add + install)
  codex   drive the Codex plugin CLI (marketplace add + install)
  omp     link the skill into ~/.omp/agent/skills (per-session discovery)
  skills  copy the bare skill folder to a destination for any Agent Skills host

The Rust renderer is NOT built at install time; the skill's step 1 builds it on
first use (clone/copy -> cargo build -> venv for PyMuPDF).
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "deckgen"
MARKETPLACE = "deckgen-plugins"


def commands(agent: str, root: Path) -> list[list[str]]:
    if agent == "codex":
        return [["codex", "plugin", "marketplace", "add", str(root)],
                ["codex", "plugin", "add", f"{NAME}@{MARKETPLACE}"]]
    if agent == "claude":
        return [["claude", "plugin", "marketplace", "add", str(root)],
                ["claude", "plugin", "install", f"{NAME}@{MARKETPLACE}"]]
    raise ValueError(agent)


def link_skill(destination: Path, *, dry_run: bool) -> None:
    source = ROOT / "skills" / NAME
    if destination.is_symlink():
        if destination.resolve() == source.resolve():
            print(f"already installed: {destination} -> {source}")
            return
        destination.unlink()
    if destination.exists():
        raise ValueError(f"destination exists and is not a link to this plugin: {destination}")
    print(shlex.join(["ln", "-s", str(source), str(destination)]), flush=True)
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.symlink_to(source)
    print(f"installed: {destination} -> {source}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=("codex", "claude", "omp", "skills"))
    parser.add_argument("--destination", type=Path,
                        help="for --agent skills only: the full destination skill folder")
    parser.add_argument("--dry-run", action="store_true", help="print actions without running them")
    parser.add_argument("--copy", action="store_true",
                        help="with --agent omp: copy instead of symlink (updates then require reinstall)")
    args = parser.parse_args(argv)

    try:
        if args.agent == "omp":
            target = Path.home() / ".omp/agent/skills" / NAME
            if args.copy:
                if target.is_symlink():
                    target.unlink()
                print(shlex.join(["cp", "-R", str(ROOT / "skills" / NAME), str(target)]), flush=True)
                if not args.dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(ROOT / "skills" / NAME, target)
                print(f"installed (copy): {target}")
            else:
                link_skill(target, dry_run=args.dry_run)
            # the loop procedure is deckgen-dev-facing but omp agents run it; keep it fresh
            loop_target = Path.home() / ".omp/agent/skills/deckgen-loop"
            loop_source = ROOT / "workflows/deckgen-loop"
            if loop_target.is_symlink() and loop_target.resolve() == loop_source.resolve():
                print(f"already installed: {loop_target} -> {loop_source}")
            elif loop_target.is_dir():
                print(shlex.join(["cp", str(loop_source / "SKILL.md"), str(loop_target / "SKILL.md")]), flush=True)
                if not args.dry_run:
                    loop_target.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(loop_source / "SKILL.md", loop_target / "SKILL.md")
                print(f"refreshed: {loop_target / 'SKILL.md'}")
            elif not loop_target.exists():
                print(shlex.join(["ln", "-s", str(loop_source), str(loop_target)]), flush=True)
                if not args.dry_run:
                    loop_target.parent.mkdir(parents=True, exist_ok=True)
                    loop_target.symlink_to(loop_source)
                print(f"installed: {loop_target} -> {loop_source}")
            else:
                raise ValueError(f"unexpected state at {loop_target}; move it aside and rerun")
            return 0

        if args.agent == "skills":
            if args.destination is None:
                parser.error("--agent skills requires --destination /path/to/skills/deckgen")
            if args.destination.name != NAME:
                parser.error(f"the destination skill folder must be named {NAME}")
            print(shlex.join(["cp", "-R", str(ROOT / "skills" / NAME), str(args.destination)]), flush=True)
            if not args.dry_run:
                args.destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(ROOT / "skills" / NAME, args.destination,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"installed: {args.destination}")
            return 0

        steps = commands(args.agent, ROOT)
        for command in steps:
            print(shlex.join(command), flush=True)
        if args.dry_run:
            return 0
        if shutil.which(args.agent) is None:
            raise ValueError(f"{args.agent} is not on PATH; install the host first, or use --dry-run")
        for command in steps:
            subprocess.run(command, check=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Installation stopped: {exc}", file=sys.stderr)
        return 1
    print("Installed. On first use the skill builds the Rust renderer (step 1 of SKILL.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
