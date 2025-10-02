#!/usr/bin/env python3
"""Spawn DocCropper in the background while redirecting logs."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
import sys
from pathlib import Path

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", required=True, help="Interpreter used to run DocCropper")
    parser.add_argument("--main", required=True, help="Path to DocCropper's main.py")
    parser.add_argument("--port", type=int, required=True, help="Port to pass to DocCropper")
    parser.add_argument("--log", required=True, help="File that will receive stdout/stderr")
    parser.add_argument("--pid-file", required=True, help="Location where the child PID will be stored")
    parser.add_argument(
        "--cwd",
        required=True,
        help="Working directory for the DocCropper process (typically the install directory)",
    )
    return parser


def launch(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    command = [args.python, args.main, "--port", str(args.port)]
    creationflags = 0
    if os.name == "nt":  # pragma: no cover - specific to Windows execution
        creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    try:
        log_file = log_path.open("a", encoding="utf-8")
    except OSError as exc:
        print(f"[launch] unable to open log file {log_path}: {exc}", file=sys.stderr)
        return 1

    with log_file:
        try:
            proc = subprocess.Popen(
                command,
                cwd=args.cwd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
        except Exception as exc:  # pragma: no cover - defensive
            log_file.write(f"[launch] failed to start DocCropper: {exc}\n")
            log_file.flush()
            print(f"[launch] failed to spawn process: {exc}", file=sys.stderr)
            return 1
        log_file.write(f"[launch] started DocCropper with PID {proc.pid}\n")
        log_file.flush()

        # Give the child process a brief moment to report immediate failures.
        time.sleep(1)
        returncode = proc.poll()
        if returncode is not None and returncode != 0:
            log_file.write(
                f"[launch] DocCropper exited immediately with code {returncode}\n"
            )
            log_file.flush()
            return 1

    try:
        Path(args.pid_file).write_text(str(proc.pid), encoding="utf-8")
    except OSError as exc:
        print(f"[launch] unable to write pid file {args.pid_file}: {exc}", file=sys.stderr)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return launch(args)


if __name__ == "__main__":
    sys.exit(main())
