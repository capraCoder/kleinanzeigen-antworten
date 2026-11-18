"""Synthetic Kleinanzeigen notification mails. Every name, ad and text here is invented."""
from email.message import EmailMessage
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

T0 = datetime(2030, 3, 1, 9, 0, tzinfo=timezone.utc)


def make_mail(cid="abc:111aaa:222bbb", sender="Anna Beispiel", text="Ist das Sofa noch da?",
              title="Sofa, grau, 3-Sitzer", nr="1234567890", kind="Nachricht", minutes=0,
              msgid=None, with_header=True, with_html=True, frm="Kleinanzeigen <noreply@mail.kleinanzeigen.de>"):
    m = EmailMessage()
    m["From"] = frm
    m["To"] = "verkaeufer@example.com"
    m["Subject"] = f'{"Re: " if kind == "Antwort" else ""}Nutzer-Anfrage zu deiner Anzeige "{title}"'
    m["Date"] = format_datetime(T0 + timedelta(minutes=minutes))
    m["Message-ID"] = msgid or f"<{cid.replace(':', '')}{minutes}@chat.kleinanzeigen.de>"
    m["References"] = f"<{cid.replace(':', '-')}@chat.kleinanzeigen.de>"
    if with_header:
        m["X-Conversation-ID"] = cid
    plain = (f"{kind} von {sender}\n\n{text}\n\n\nZur Anzeige: {title} (Anzeigennummer: {nr})\n"
             "Antworte direkt in der App oder auf kleinanzeigen.de.")
    cs = "iso-8859-1" if all(ord(c) < 256 for c in plain) else "utf-8"  # Kleinanzeigen uses latin-1
    m.set_content(plain, charset=cs, cte="quoted-printable")
    if with_html:
        body = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br />")
        # Same shape as the real mails (2026): bold "von" line, two <br>, text in a <p> in a grey cell.
        rich = (f'<html><body><table><tr><td>\r\n  {kind} zur Anzeige "{title}"\r\n</td></tr>'
                f'<tr><td>(Anzeigennummer: {nr}) erhalten.<br/><br/><table><tr>'
                f'<td valign="top" bgcolor="#f0f0f0" style="background-color: #f0f0f0;">\r\n'
                f'<p style="margin: 0;">\r\n    <b>{kind} von</b> {sender}\r\n    \r\n    <br><br>\r\n'
                f'    {body}\r\n</p>\r\n</td></tr></table>'
                f'<a class="cta-button" href="https://www.kleinanzeigen.de/m-nachrichten.html?conversationId={cid}">'
                f'Antworten</a></td></tr></table></body></html>')
        m.add_alternative(rich, subtype="html", charset=cs, cte="quoted-printable")
    return m


def system_mail():
    """A Kleinanzeigen mail that is not a buyer message (no conversation)."""
    m = EmailMessage()
    m["From"] = "Kleinanzeigen <noreply@mail.kleinanzeigen.de>"
    m["Subject"] = "Deine Anzeige ist jetzt online"
    m["Date"] = format_datetime(T0)
    m["Message-ID"] = "<system1@mail.kleinanzeigen.de>"
    m.set_content("Deine Anzeige ist jetzt online.", charset="iso-8859-1", cte="quoted-printable")
    return m


def demo_set():
    """A small invented inbox for the screenshot and the demo page."""
    return [
        make_mail("aaa:1:1", "Anna Beispiel", "Hallo, ist das Sofa noch da? Ich könnte Samstag kommen.", minutes=0),
        make_mail("aaa:1:1", "Anna Beispiel", "Super, dann 11 Uhr? Wie ist die Adresse?", kind="Antwort", minutes=90),
        make_mail("bbb:2:2", "Bernd Muster", "Würden Sie 40 € nehmen? Versand mit DHL wäre toll.", minutes=30),
        make_mail("ccc:3:3", "Privat", "Zahle sofort per PayPal, schreib mir auf WhatsApp +49 151 23456789",
                  minutes=45),
        make_mail("ddd:4:4", "Carla Probe", "Ist das Fahrrad noch zu haben?", title="Kinderfahrrad 20 Zoll",
                  nr="1234567891", minutes=60),
        make_mail("eee:5:5", "Bernd Muster", "Nehme das Fahrrad auch, wenn es noch da ist.",
                  title="Kinderfahrrad 20 Zoll", nr="1234567891", minutes=75),
    ]


if __name__ == "__main__":  # writes tests/demo.mbox
    import mailbox
    from pathlib import Path
    p = Path(__file__).with_name("demo.mbox")
    p.unlink(missing_ok=True)
    box = mailbox.mbox(str(p))
    for msg in demo_set():
        box.add(msg)
    box.close()
    print(p)
