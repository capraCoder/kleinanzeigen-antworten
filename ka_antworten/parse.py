"""Read Kleinanzeigen notification e-mails and turn each buyer message into a plain dict.

Only the e-mails Kleinanzeigen sends you are read. Nothing here logs in to Kleinanzeigen,
calls its servers or sends anything.

Sources: .eml files, .mbox files (Thunderbird, Gmail Takeout), folders of those, or an
IMAP mailbox opened READ-ONLY (messages are fetched with BODY.PEEK, so they stay unread).
"""
from __future__ import annotations

import html
import imaplib
import mailbox
import re
from datetime import date, timedelta
from email import message_from_binary_file, message_from_bytes
from email.message import EmailMessage
from email.policy import default as POLICY
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, Iterator

SENDER_DOMAIN = "kleinanzeigen.de"
RX_TITLE = re.compile(r'Anzeige\s*[„"](.+?)["“]\s*$', re.S)
RX_NR = re.compile(r"Anzeigennummer:\s*(\d+)")
# The HTML part carries the sender name in bold, then two line breaks, then the text.
RX_HEAD = re.compile(
    r"<b>\s*(Antwort|Nachricht)\s+von\s*</b>\s*(.*?)\s*(?:<br\s*/?>\s*){2}(.*?)</td>",
    re.I | re.S,
)
RX_PLAIN_HEAD = re.compile(r"^\s*(Antwort|Nachricht) von\s*(.+?)\s*$", re.M)
RX_REF_CID = re.compile(r"<([\w]+)-([\w]+)-([\w]+)@chat\.kleinanzeigen\.de>")
RX_LINK_CID = re.compile(r"conversationId=([\w:%-]+)")
RX_TAG = re.compile(r"<[^>]+>")
RX_BR = re.compile(r"<br\s*/?>|</p>|</div>", re.I)


def _html_to_text(fragment: str) -> str:
    t = RX_TAG.sub("", RX_BR.sub("\n", fragment))
    lines = [ln.strip() for ln in html.unescape(t).replace("\xa0", " ").splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _bodies(msg: EmailMessage) -> tuple[str, str]:
    plain = rich = ""
    for part in msg.walk():
        if part.is_multipart():
            continue
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html"):
            continue
        try:
            body = part.get_content()
        except (LookupError, ValueError):
            raw = part.get_payload(decode=True) or b""
            body = raw.decode(part.get_content_charset() or "latin-1", "replace")
        if ctype == "text/plain" and not plain:
            plain = body
        elif ctype == "text/html" and not rich:
            rich = body
    return plain, rich


def conversation_id(msg: EmailMessage, rich: str = "") -> str:
    """X-Conversation-ID header, else the References header, else the "Antworten" button link."""
    cid = str(msg.get("X-Conversation-ID", "") or "").strip()
    if cid:
        return cid
    m = RX_REF_CID.search(str(msg.get("References", "") or ""))
    if m:
        return ":".join(m.groups())
    m = RX_LINK_CID.search(rich)
    return m.group(1).replace("%3A", ":").replace("%3a", ":") if m else ""


def parse_message(msg: EmailMessage) -> dict | None:
    """One buyer message as a dict, or None for anything that is not one (system mail, other sender)."""
    if SENDER_DOMAIN not in str(msg.get("From", "")).lower():
        return None
    plain, rich = _bodies(msg)
    cid = conversation_id(msg, rich)
    if not cid:
        return None
    kind = sender = text = ""
    m = RX_HEAD.search(rich)
    if m:
        kind, sender, text = m.group(1), _html_to_text(m.group(2)), _html_to_text(m.group(3))
    else:  # no usable HTML: the name is the rest of the "Antwort von ..." line, the text follows
        mp = RX_PLAIN_HEAD.search(plain)
        if not mp:
            return None
        kind, sender = mp.group(1), mp.group(2)
        text = plain[mp.end():].strip().split("\n\n\n")[0].strip()
    if not sender:
        return None
    subject = str(msg.get("Subject", "") or "")
    t = RX_TITLE.search(subject)
    nr = RX_NR.search(plain) or RX_NR.search(_html_to_text(rich))
    try:
        when = parsedate_to_datetime(str(msg.get("Date"))).isoformat()
    except (TypeError, ValueError):
        when = ""
    return {
        "id": str(msg.get("Message-ID", "") or "").strip() or f"{cid}|{when}|{sender}",
        "conv": cid,
        "date": when,
        "nr": nr.group(1) if nr else "",
        "title": t.group(1).strip() if t else "",
        "kind": "antwort" if kind.lower() == "antwort" else "nachricht",
        "sender": sender,
        "text": text,
    }


def read_eml(path: Path) -> EmailMessage:
    with open(path, "rb") as f:
        return message_from_binary_file(f, policy=POLICY)


def read_mbox(path: Path) -> Iterator[EmailMessage]:
    box = mailbox.mbox(str(path), factory=lambda f: message_from_binary_file(f, policy=POLICY), create=False)
    try:
        yield from box
    finally:
        box.close()


def messages_from_paths(paths: Iterable[str | Path]) -> Iterator[EmailMessage]:
    for p in map(Path, paths):
        if p.is_dir():
            yield from messages_from_paths(sorted(x for x in p.rglob("*") if x.suffix.lower() in (".eml", ".mbox")))
        elif p.suffix.lower() == ".mbox":
            yield from read_mbox(p)
        elif p.is_file():
            yield read_eml(p)
        else:
            raise FileNotFoundError(p)


_MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def messages_from_imap(host: str, user: str, password: str, folder: str = "INBOX",
                       days: int = 14, port: int = 993) -> Iterator[EmailMessage]:
    """Fetch Kleinanzeigen mails READ-ONLY: the folder is opened with readonly=True and
    BODY.PEEK[] is used, so no flag (not even "seen") is changed on the server."""
    since = date.today() - timedelta(days=days)
    since_s = f"{since.day:02d}-{_MONTHS[since.month - 1]}-{since.year}"  # IMAP wants English months
    with imaplib.IMAP4_SSL(host, port) as M:
        M.login(user, password)
        typ, _ = M.select(f'"{folder}"', readonly=True)
        if typ != "OK":
            raise RuntimeError(f"IMAP folder not found: {folder}")
        typ, data = M.search(None, "FROM", f'"{SENDER_DOMAIN}"', "SINCE", since_s)
        for num in (data[0] or b"").split():
            typ, d = M.fetch(num, "(BODY.PEEK[])")
            if typ == "OK" and d and isinstance(d[0], tuple):
                yield message_from_bytes(d[0][1], policy=POLICY)


def parse_all(msgs: Iterable[EmailMessage]) -> tuple[list[dict], int]:
    """Buyer messages (deduplicated by Message-ID, oldest first) and the count of skipped mails."""
    seen, out, skipped = set(), [], 0
    for msg in msgs:
        r = parse_message(msg)
        if r is None:
            skipped += 1
            continue
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    out.sort(key=lambda r: r["date"])
    return out, skipped
