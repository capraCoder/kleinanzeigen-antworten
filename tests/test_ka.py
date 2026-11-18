import json
import mailbox
import re
import tempfile
import unittest
from email import message_from_bytes
from email.policy import default as POLICY
from pathlib import Path

from ka_antworten.__main__ import main
from ka_antworten.build import hints, render, short_name, to_messages
from ka_antworten.parse import messages_from_paths, parse_all, parse_message
from tests.fake import demo_set, make_mail, system_mail


def roundtrip(msg):
    """Serialise and re-read, as a real .eml file would be."""
    return message_from_bytes(msg.as_bytes(), policy=POLICY)


class Parse(unittest.TestCase):
    def test_first_message(self):
        r = parse_message(roundtrip(make_mail(text="Grüße aus Köln, ist es noch da?")))
        self.assertEqual(r["conv"], "abc:111aaa:222bbb")
        self.assertEqual(r["sender"], "Anna Beispiel")
        self.assertEqual(r["text"], "Grüße aus Köln, ist es noch da?")  # iso-8859-1 QP decoded
        self.assertEqual(r["nr"], "1234567890")
        self.assertEqual(r["title"], "Sofa, grau, 3-Sitzer")
        self.assertEqual(r["kind"], "nachricht")

    def test_reply_multiline(self):
        r = parse_message(roundtrip(make_mail(kind="Antwort", text="Zeile 1\nZeile 2 & <mehr>")))
        self.assertEqual(r["kind"], "antwort")
        self.assertEqual(r["text"], "Zeile 1\nZeile 2 & <mehr>")

    def test_plain_only_fallback(self):
        r = parse_message(roundtrip(make_mail(with_html=False, sender="Bernd Muster", text="Noch da?")))
        self.assertEqual((r["sender"], r["text"]), ("Bernd Muster", "Noch da?"))

    def test_conversation_id_from_references(self):
        r = parse_message(roundtrip(make_mail(cid="w1:x2:y3", with_header=False)))
        self.assertEqual(r["conv"], "w1:x2:y3")

    def test_conversation_id_from_button_link(self):
        m = make_mail(cid="q7:r8:s9", with_header=False)
        del m["References"]
        self.assertEqual(parse_message(roundtrip(m))["conv"], "q7:r8:s9")

    # negative controls: these must NOT become buyer messages
    def test_system_mail_rejected(self):
        self.assertIsNone(parse_message(roundtrip(system_mail())))

    def test_other_sender_rejected(self):
        self.assertIsNone(parse_message(roundtrip(make_mail(frm="Phisher <info@kleinanzeigen-sicher.example>"))))


class Files(unittest.TestCase):
    def test_mbox_and_eml_dedupe(self):
        with tempfile.TemporaryDirectory() as d:
            box = mailbox.mbox(str(Path(d, "a.mbox")))
            for m in demo_set() + [system_mail()]:
                box.add(m)
            box.close()
            Path(d, "dup.eml").write_bytes(demo_set()[0].as_bytes())  # same Message-ID again
            rows, skipped = parse_all(messages_from_paths([d]))
        self.assertEqual(len(rows), 6)
        self.assertEqual(skipped, 1)
        self.assertEqual(len({r["conv"] for r in rows}), 5)


class Build(unittest.TestCase):
    def rows(self):
        return parse_all(roundtrip(m) for m in demo_set())[0]

    def test_short_name(self):
        self.assertEqual(short_name("Anna Beispiel"), "Anna B.")
        self.assertEqual(short_name("Privat"), "Privat")

    def test_generic_names_never_merge(self):
        rows = self.rows() + parse_all([roundtrip(make_mail("zzz:9:9", "Privat", "Hallo", minutes=5))])[0]
        wks = {m["wk"] for m in to_messages(rows) if m["who"] == "Privat"}
        self.assertEqual(len(wks), 2)

    def test_unknown_timezone_falls_back(self):
        self.assertEqual(len(to_messages(self.rows(), tz="Nirgendwo/Gibtsnicht")), 6)

    def test_hints(self):
        h = hints(to_messages(self.rows()))
        self.assertIn("Versand/Kurier gefragt", h["bbb:2:2"])
        self.assertIn("Preisangebot: 40 €", h["bbb:2:2"])
        self.assertIn("PayPal/Vorkasse erwähnt", h["ccc:3:3"])
        self.assertIn("Telefonnummer im Text", h["ccc:3:3"])
        self.assertIn("gleicher Name in 2 Gesprächen", h["eee:5:5"])
        self.assertEqual(h["ddd:4:4"], [])  # negative control: harmless text, no hint

    def test_render_is_safe_and_complete(self):
        evil = parse_all([roundtrip(make_mail("x:1:1", "Eve Test", "</script><script>alert(1)</script>"))])[0]
        page = render(self.rows() + evil, {"title": "Test <b>", "ads": {"1234567890": "Sofa"}})
        self.assertNotRegex(page, r"__[A-Z]+__")
        self.assertEqual(page.count("</script>"), 2)  # only the two real closing tags
        self.assertIn("Test &lt;b&gt;", page)
        data = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', page, re.S).group(1))
        self.assertEqual(len(data), 7)


class Cli(unittest.TestCase):
    def test_cli_writes_page(self):
        with tempfile.TemporaryDirectory() as d:
            for i, m in enumerate(demo_set()):
                Path(d, f"{i}.eml").write_bytes(m.as_bytes())
            out = Path(d, "out.html")
            self.assertEqual(main([d, "--config", str(Path(d, "none.toml")), "--out", str(out)]), 0)
            self.assertIn("Anna B.", out.read_text(encoding="utf-8"))

    def test_cli_empty_fails(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "s.eml").write_bytes(system_mail().as_bytes())
            self.assertEqual(main([d, "--out", str(Path(d, "o.html"))]), 1)


if __name__ == "__main__":
    unittest.main()
