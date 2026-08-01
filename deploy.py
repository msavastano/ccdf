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
import fnmatch
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def notes_assets() -> list[Path]:
    """Sibling pages the notes pack links to.

    Read straight out of build-notes-pack.py's WALKTHROUGHS registry so the two
    lists cannot drift — adding a walkthrough there is enough to have it
    deployed here. Importing the build script is side-effect free; it only
    builds under `if __name__ == "__main__"`.
    """
    builder = ROOT / "build-notes-pack.py"
    spec = importlib.util.spec_from_file_location("_build_notes_pack", builder)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # A walkthrough covering two skills is registered twice; stage it once.
    names = dict.fromkeys(w["file"] for w in module.WALKTHROUGHS)
    return [ROOT / name for name in names]

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
        # Copied beside index.html so the notes pack's relative links resolve
        # the same way deployed as they do from the repo root.
        "assets": notes_assets,
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


def not_uploadable(stage_dir: Path, names: list[str]) -> list[str]:
    """Which of `names` .vercelignore would keep out of the upload.

    The stage folders use an allowlist (`/*`, then `!name` lines), so a file can
    sit in the staged folder and still never reach Vercel. That failure is
    invisible — the deploy reports success and the page 404s — so the stage step
    checks for it rather than trusting that copying was enough.

    Only allowlist-style files are checked; a plain denylist has nothing to
    verify here and returns no complaints.
    """
    ignore = stage_dir / ".vercelignore"
    if not ignore.exists():
        return []
    lines = [
        line.strip()
        for line in ignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not any(line in ("/*", "*") for line in lines):
        return []
    allowed = [line[1:] for line in lines if line.startswith("!")]
    return [n for n in names if not any(fnmatch.fnmatch(n, p) for p in allowed)]


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

    assets = target.get("assets") or []
    if callable(assets):
        assets = assets()
    for asset in assets:
        if not asset.exists():
            sys.exit(
                f"{asset.name} is linked from {source.name} but was not found. "
                f"Deploying without it would publish a broken link."
            )
        asset_dest = stage_dir / asset.name
        shutil.copyfile(asset, asset_dest)
        print(
            f"Staged {asset.name} -> {asset_dest.relative_to(ROOT).as_posix()} "
            f"({asset_dest.stat().st_size:,} bytes)"
        )

    blocked = not_uploadable(stage_dir, ["index.html"] + [a.name for a in assets])
    if blocked:
        listed = "\n  ".join(blocked)
        sys.exit(
            f"\n{stage_dir.relative_to(ROOT).as_posix()}/.vercelignore would exclude "
            f"these staged file(s) from the upload:\n  {listed}\n\n"
            f"They would 404 in production while the deploy reported success. "
            f"Add a matching '!' line to that allowlist."
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
