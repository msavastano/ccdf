#!/usr/bin/env python3
"""Build and deploy the two generated study pages to Vercel as separate projects.

Each page is a single self-contained HTML file. This script stages it as
`deploy/<project>/index.html` and hands that folder to the Vercel CLI, so the
two pages live as two independent Vercel projects out of one repo.

Usage
-----
    python deploy.py                  # stage both, deploy both to preview
    python deploy.py hub              # only the study hub
    python deploy.py notes --prod     # only the notes pack, to production
    python deploy.py --build          # rebuild the HTML first, then deploy
    python deploy.py --stage-only     # stage the files, skip the deploy

First run per project is interactive: the Vercel CLI asks which scope to use
and what to name the project. After that the link is remembered in
`deploy/<project>/.vercel/` (gitignored) and deploys run unattended.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

TARGETS = {
    "hub": {
        "source": ROOT / "study-hub.html",
        "stage": ROOT / "deploy" / "study-hub",
        "builder": ROOT / "build-study-hub.py",
        "label": "Study Hub",
    },
    "notes": {
        "source": ROOT / "notes-pack.html",
        "stage": ROOT / "deploy" / "notes-pack",
        "builder": ROOT / "build-notes-pack.py",
        "label": "Notes Pack",
    },
}


def vercel_cmd() -> str:
    """Locate the Vercel CLI (vercel.cmd on Windows)."""
    for name in ("vercel", "vercel.cmd"):
        found = shutil.which(name)
        if found:
            return found
    sys.exit(
        "Vercel CLI not found on PATH.\n"
        "Install it with:  npm i -g vercel\n"
        "Then sign in with: vercel login"
    )


def build(target: dict) -> None:
    """Run the target's build script."""
    builder = target["builder"]
    print(f"\n=== Building {target['label']} ({builder.name}) ===", flush=True)
    result = subprocess.run([sys.executable, str(builder)], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"Build failed for {target['label']} (exit {result.returncode}).")


def stage(target: dict) -> Path:
    """Copy the built HTML into the project's deploy folder as index.html."""
    source = target["source"]
    if not source.exists():
        sys.exit(
            f"{source.name} not found. Run `python {target['builder'].name}` first, "
            f"or pass --build."
        )

    stage_dir = target["stage"]
    stage_dir.mkdir(parents=True, exist_ok=True)
    dest = stage_dir / "index.html"
    shutil.copyfile(source, dest)
    print(
        f"Staged {source.name} -> {dest.relative_to(ROOT).as_posix()} "
        f"({dest.stat().st_size:,} bytes)"
    )
    return stage_dir


def deploy(target: dict, stage_dir: Path, prod: bool) -> None:
    """Hand the staged folder to the Vercel CLI."""
    cli = vercel_cmd()
    linked = (stage_dir / ".vercel" / "project.json").exists()

    cmd = [cli, "deploy", "--cwd", str(stage_dir)]
    if prod:
        cmd.append("--prod")
    if linked:
        # Already linked: no prompts needed.
        cmd.append("--yes")
    else:
        print(
            f"\n{target['label']} is not linked to a Vercel project yet - "
            f"the CLI will ask you to pick a scope and project name."
        )

    env = "production" if prod else "preview"
    print(f"\n=== Deploying {target['label']} to {env} ===")
    print("  " + " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"Deploy failed for {target['label']} (exit {result.returncode}).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and deploy the study pages to Vercel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "targets",
        nargs="*",
        choices=["hub", "notes", "all"],
        help="Which page(s) to handle: hub, notes, or all. Default: all.",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Deploy to production instead of a preview URL.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Run the build script before staging.",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="Stage the files but do not call Vercel.",
    )
    args = parser.parse_args()

    requested = args.targets or ["all"]
    names = ["hub", "notes"] if "all" in requested else list(dict.fromkeys(requested))

    for name in names:
        target = TARGETS[name]
        if args.build:
            build(target)
        stage_dir = stage(target)
        if not args.stage_only:
            deploy(target, stage_dir, args.prod)

    if args.stage_only:
        print("\nStaged only - nothing deployed.")
    else:
        print("\nDone.")


if __name__ == "__main__":
    main()
