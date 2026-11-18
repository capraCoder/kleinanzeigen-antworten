"""Turn parsed buyer messages into one self-contained HTML page (no server, no network)."""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from importlib.resources import files
from zoneinfo import ZoneInfo

TITLE_SALUTATION = {"fr", "frau", "hr", "herr"}
GENERIC = {"privat", "nutzer", "kleinanzeigen-nutzer", "fr", "frau", "hr", "herr", ""}


def short_name(s: str) -> str:
    """First name plus initial: 'Anna Beispiel' -> 'Anna B.', 'Frau Muster' -> 'Frau M.'."""
    t = (s or "").strip().split()
    if len(t) < 2:
        return " ".join(t)
    return f"{t[0]} {t[1][0]}."


def norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().rstrip(".")).casefold()


# Rule-based hints shown on each conversation. Plain patterns, no AI.
RULES = [
    (re.compile(r"paypal|vorkasse|überweis|anzahlung", re.I), "PayPal/Vorkasse erwähnt"),
    (re.compile(r"\bversand|verschick|zuschicken|\bdhl\b|hermes|\bdpd\b|kurier|spedition", re.I), "Versand/Kurier gefragt"),
    (re.compile(r"https?://|www\.|wa\.me|whats ?app|telegram", re.I), "Link/Messenger: nicht klicken"),
    (re.compile(r"(?:\+49|(?<!\d)0)\s?1\d[\d\s/-]{7,}"), "Telefonnummer im Text"),
    (re.compile(r"\badresse|hausnummer", re.I), "fragt nach Adresse"),
]
PRICE = re.compile(r"(?<![\d.,])(\d{1,5})\s?(?:€|euro\b|eur\b)", re.I)


def to_messages(rows: list[dict], tz: str = "Europe/Berlin", full_names: bool = False) -> list[dict]:
    zone = ZoneInfo(tz)
    out = []
    for r in rows:
        who = r["sender"].strip() if full_names else short_name(r["sender"])
        wk = norm_name(who)
        if wk in GENERIC:  # placeholder names are never merged across conversations
            wk = f"{wk}#{r['conv']}"
        ts = datetime.fromisoformat(r["date"]).astimezone(zone).isoformat() if r["date"] else ""
        out.append({"id": r["id"], "ts": ts, "nr": r["nr"], "ad": r["title"], "kind": r["kind"],
                    "who": who, "wk": wk, "conv": r["conv"], "text": r["text"]})
    out.sort(key=lambda m: m["ts"])
    return out


def hints(msgs: list[dict]) -> dict[str, list[str]]:
    by_conv, convs_of = {}, {}
    for m in msgs:
        by_conv.setdefault(m["conv"], []).append(m)
        if "#" not in m["wk"]:
            convs_of.setdefault(m["wk"], set()).add(m["conv"])
    out = {}
    for conv, ms in by_conv.items():
        text = " ".join(m["text"] for m in ms)
        h = [label for rx, label in RULES if rx.search(text)]
        prices = sorted({int(p) for p in PRICE.findall(text)})
        if prices:
            h.append("Preisangebot: " + ", ".join(f"{p} €" for p in prices))
        n = len(convs_of.get(ms[0]["wk"], ()))
        if n > 1:
            h.append(f"gleicher Name in {n} Gesprächen")
        out[conv] = h
    return out


def _js(obj) -> str:
    """JSON safe to embed inside <script>: no '</' can close the tag early."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")


def render(rows: list[dict], config: dict) -> str:
    tz = config.get("timezone", "Europe/Berlin")
    msgs = to_messages(rows, tz, bool(config.get("full_names", False)))
    ads = {str(k): str(v) for k, v in (config.get("ads") or {}).items()}
    for m in msgs:
        ads.setdefault(m["nr"], m["ad"])
    replies = [[r["label"], r["text"]] for r in (config.get("replies") or [])]
    deadline = config.get("deadline") or None
    stamp = datetime.now(timezone.utc).astimezone(ZoneInfo(tz)).strftime("%d.%m.%Y %H:%M")
    page = files("ka_antworten").joinpath("page.html").read_text(encoding="utf-8")
    subs = {
        "__TITLE__": html.escape(config.get("title", "Kleinanzeigen-Antworten")),
        "__DATA__": _js(msgs),
        "__ADS__": _js(ads),
        "__REPLIES__": _js(replies),
        "__AUTO__": _js(hints(msgs)),
        "__DEADLINE__": _js(deadline),
        "__STAMP__": html.escape(stamp),
        "__NMSG__": str(len(msgs)),
        "__NCONV__": str(len({m["conv"] for m in msgs})),
        "__NBUY__": str(len({m["wk"] for m in msgs})),
    }
    for k, v in subs.items():
        page = page.replace(k, v)
    return page
