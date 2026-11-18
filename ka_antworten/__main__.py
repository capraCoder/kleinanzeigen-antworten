"""ka-antworten: read Kleinanzeigen notification e-mails, write a local reply page.

  ka-antworten Postfach.mbox                 # .eml / .mbox files or folders
  ka-antworten --imap                        # read-only IMAP, settings from config.toml
  ka-antworten --config mein.toml --out antworten.html export/
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
import tomllib
from pathlib import Path

from . import __version__
from .build import render
from .parse import messages_from_imap, messages_from_paths, parse_all


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ka-antworten", description=__doc__.split("\n")[0])
    ap.add_argument("inputs", nargs="*", help=".eml or .mbox files, or folders containing them")
    ap.add_argument("--imap", action="store_true", help="read the mailbox over IMAP (read-only)")
    ap.add_argument("--config", default="config.toml", help="settings file (default: config.toml)")
    ap.add_argument("--out", default="antworten.html", help="output page (default: antworten.html)")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)

    cfg_path = Path(a.config)
    config = tomllib.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    if not a.inputs and not a.imap:
        ap.error("give .eml/.mbox files or folders, or --imap")

    sources = []
    if a.inputs:
        sources.append(messages_from_paths(a.inputs))
    if a.imap:
        im = config.get("imap") or {}
        if not im.get("host") or not im.get("user"):
            ap.error(f"--imap needs [imap] host and user in {cfg_path}")
        password = os.environ.get("KA_IMAP_PASSWORD") or getpass.getpass(f"IMAP-Passwort für {im['user']}: ")
        sources.append(messages_from_imap(im["host"], im["user"], password, im.get("folder", "INBOX"),
                                          int(im.get("days", 14)), int(im.get("port", 993))))

    rows, skipped = parse_all(m for src in sources for m in src)
    if not rows:
        print(f"Keine Käufer-Nachrichten gefunden ({skipped} andere Mails übersprungen).", file=sys.stderr)
        return 1
    Path(a.out).write_text(render(rows, config), encoding="utf-8")
    print(f"OK {len(rows)} Nachrichten in {len({r['conv'] for r in rows})} Gesprächen, "
          f"{skipped} andere Mails übersprungen -> {Path(a.out).resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
