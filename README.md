# kleinanzeigen-antworten

**Deutsch** · [English](#english)

Ein lokaler Antwort-Schreibtisch für Verkäufer auf Kleinanzeigen. Das Programm liest die
Benachrichtigungs-E-Mails, die Kleinanzeigen dir bei jeder Käufer-Nachricht schickt, und baut
daraus **eine einzige HTML-Seite**: alle Gespräche nach Anzeige sortiert, ungelesene oben,
Warnhinweise (PayPal, Versand, Telefonnummer, Links), Antwortvorlagen, und ein Knopf pro
Gespräch, der genau dieses Gespräch auf kleinanzeigen.de öffnet. Dort antwortest du selbst.

Es gibt andere Werkzeuge für Kleinanzeigen. Was unseres anders macht: es liest nur die
Benachrichtigungs-E-Mails, braucht also kein Login, birgt kein Kontorisiko und berührt
Kleinanzeigen nie.

- Kein Kleinanzeigen-Login, kein Scraping, keine Automatisierung der Website.
- Keine Abhängigkeiten: nur Python 3.11 oder neuer.
- Alles bleibt auf deinem Rechner. Die Seite lädt nichts nach.
- IMAP wird **nur lesend** geöffnet (`readonly`, `BODY.PEEK`): nicht einmal "gelesen" wird gesetzt.

## Installation

```bash
pip install git+https://github.com/capraCoder/kleinanzeigen-antworten
```

## Benutzung

Aus exportierten Mails (.eml, .mbox, oder ein Ordner davon, z. B. aus Thunderbird oder Google Takeout):

```bash
ka-antworten ~/Downloads/kleinanzeigen.mbox --out antworten.html
```

Direkt aus dem Postfach (nur lesend). Trage `[imap]` in `config.toml` ein; das Passwort kommt aus
der Umgebungsvariable `KA_IMAP_PASSWORD` oder wird abgefragt, nie aus der Datei. Bei Gmail ein
App-Passwort verwenden.

```bash
ka-antworten --imap --config config.toml
```

Vorlagen, Anzeigennamen und einen optionalen Countdown stellst du in `config.toml` ein
(Vorlage: `config.example.toml`). Ausprobieren ohne eigene Mails:

```bash
python -m tests.fake && ka-antworten tests/demo.mbox --out demo.html
```

## Datenschutz

Die erzeugte HTML-Datei enthält Namen und Nachrichten deiner Käufer. Teile sie nicht; die
`.gitignore` schließt `*.html`, `config.toml` und Mail-Exporte aus. Standardmäßig wird der
Nachname abgekürzt ("Anna B.").

Dieses Projekt ist nicht mit Kleinanzeigen verbunden. "Kleinanzeigen" ist eine Marke ihres Inhabers.

---

## English

A local reply desk for sellers on Kleinanzeigen (Germany's largest classifieds site). It reads the
notification e-mails Kleinanzeigen sends you for every buyer message and builds **one HTML page**:
conversations grouped by ad, unread first, warning hints (PayPal, shipping, phone numbers, links),
reply templates, and one button per conversation that opens exactly that conversation on
kleinanzeigen.de, where you reply yourself.

What makes ours different is that it only reads the notification emails, so it needs no login,
takes no account risk and never touches Kleinanzeigen.

- No Kleinanzeigen login, no scraping, no site automation.
- No dependencies: Python 3.11 or later.
- Everything stays on your machine; the page loads nothing from the network.
- IMAP is opened **read-only** (`readonly`, `BODY.PEEK`): not even the "seen" flag changes.

Install with `pip install git+https://github.com/capraCoder/kleinanzeigen-antworten`, then run
`ka-antworten <files-or-folders> --out antworten.html` or `ka-antworten --imap --config config.toml`
(password from `KA_IMAP_PASSWORD` or a prompt, never from the file). Tests: `python -m unittest`.

The generated page contains your buyers' names and messages; do not share it. Not affiliated with
Kleinanzeigen. MIT licence.
