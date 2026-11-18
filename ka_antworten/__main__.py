"""ka-antworten: read Kleinanzeigen notification e-mails, write a local reply page.

  ka-antworten Postfach.mbox                 # .eml / .mbox files or folders
  ka-antworten --imap                        # read-only IMAP, settings from config.toml
  ka-antworten --config mein.toml --out antworten.html export/
  ka-antworten                               # easy mode: folder "Kleinanzeigen" on the desktop
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
import tomllib
import webbrowser
from pathlib import Path

from . import __version__
from .build import render
from .parse import messages_from_imap, messages_from_paths, parse_all


FOLDER = "Kleinanzeigen"


def _desktops() -> list[Path]:
    home = Path.home()
    cands = [home / "Desktop", home / "OneDrive" / "Desktop", home / "OneDrive" / "Schreibtisch", home / "Schreibtisch"]
    cands += sorted(home.glob("OneDrive*/Desktop"))
    return [c for c in cands if c.is_dir()]


def find_folder() -> Path:
    """Easy mode: a "Kleinanzeigen" folder next to the program or on the desktop (created if missing)."""
    here = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd()
    places = [here] + _desktops()
    for p in places:
        if (p / FOLDER).is_dir():
            return p / FOLDER
    target = (_desktops() or [here])[0] / FOLDER
    target.mkdir(parents=True, exist_ok=True)
    return target


def easy() -> int:
    """Double-click mode: no options, build the page from the folder and open it."""
    folder = find_folder()
    print(f"Ordner: {folder}")
    if not any(x.suffix.lower() in (".eml", ".mbox") for x in folder.rglob("*")):
        print("Der Ordner ist noch leer. Lege Deine Kleinanzeigen-Mails hinein (siehe Anleitung)"
              " und starte das Programm dann noch einmal.")
        return 1
    out = folder.parent / "antworten.html"
    cfg = folder / "config.toml"
    rc = main([str(folder), "--out", str(out)] + (["--config", str(cfg)] if cfg.exists() else ["--config", str(folder / "-")]))
    if rc == 0:
        webbrowser.open(out.as_uri())
    return rc


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


def entry() -> int:
    """Console entry: with no arguments run easy mode; keep a double-clicked window open."""
    rc = easy() if len(sys.argv) == 1 else main()
    if getattr(sys, "frozen", False) and len(sys.argv) == 1:
        input("\nEnter drücken zum Schließen ...")
    return rc


if __name__ == "__main__":
    sys.exit(entry())
