#!/usr/bin/env python3
"""Install the `star` command, which runs spin.py from any directory.

Usage:
  python3 init.py                         # install `star` into ~/.local/bin
  python3 init.py --dir /usr/local/bin    # install system-wide (may need sudo)
  python3 init.py --name spin             # use a different command name
  python3 init.py --force                 # overwrite an existing unrelated command
  python3 init.py --uninstall             # remove the launcher again

After installing, all arguments are passed straight to spin.py:
  star
  star -c magenta
  star -c green -s '@'
"""

import argparse
import os
import shlex
import shutil
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPIN = HERE.parent / "main.py"
MARKER = "# installed by init.py"  

def parse_args():
    parser = argparse.ArgumentParser(description="Install the `star` command for main.py .")
    parser.add_argument("--name", default="star",
                        help="command name to install (default: star)")
    parser.add_argument("--dir", default="~/.local/bin",
                        help="directory to put the command in (default: ~/.local/bin)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing file that was not installed by this script")
    parser.add_argument("--uninstall", action="store_true",
                        help="remove the command instead of installing it")
    args = parser.parse_args()
    if "/" in args.name or args.name in ("", ".", ".."):
        parser.error("--name must be a plain command name without slashes")
    return args


def build_launcher(python, script):
    """A tiny shell script that runs main.py with the same interpreter and forwards all arguments."""
    return (
        "#!/bin/sh\n"
        f"{MARKER}\n"
        f'exec {shlex.quote(python)} {shlex.quote(str(script))} "$@"\n'
    )


def path_warning(target_dir):
    """Tell the user how to add the directory to PATH if it is missing."""
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if str(target_dir) in path_dirs:
        return
    print(f"\nNote: {target_dir} is not in your PATH yet. Add this line to ~/.bashrc or ~/.zshrc:")
    print(f'  export PATH="{target_dir}:$PATH"')
    print("then open a new terminal.")


def install(args):
    if not SPIN.is_file():
        sys.exit(f"error: main.py not found next to init.py (expected {SPIN})")

    target_dir = Path(args.dir).expanduser()
    target = target_dir / args.name

    if target.exists() and not args.force:
        if MARKER not in target.read_text(errors="ignore"):
            sys.exit(f"error: {target} already exists and was not installed by init.py. "
                     "Use --force to overwrite it or --name to pick another name.")

    existing = shutil.which(args.name)
    if existing and Path(existing).resolve() != target.resolve():
        print(f"warning: another '{args.name}' command already exists at {existing}")

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(build_launcher(sys.executable, SPIN))
        mode = target.stat().st_mode
        target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except PermissionError:
        sys.exit(f"error: no permission to write to {target_dir}. "
                 "Try --dir ~/.local/bin, or run with sudo for a system directory.")

    print(f"Installed '{args.name}' -> {target}")
    print(f"Run it with:  {args.name}   (arguments go to main.py, e.g. {args.name} -c magenta)")
    path_warning(target_dir)


def uninstall(args):
    target = Path(args.dir).expanduser() / args.name
    if not target.exists():
        sys.exit(f"nothing to remove: {target} does not exist")
    if MARKER not in target.read_text(errors="ignore"):
        sys.exit(f"error: {target} was not installed by init.py, leaving it alone")
    target.unlink()
    print(f"Removed {target}")


def main():
    args = parse_args()
    if args.uninstall:
        uninstall(args)
    else:
        install(args)


if __name__ == "__main__":
    main()