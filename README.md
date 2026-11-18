# kleinanzeigen-antworten

> **Kurz erklärt**
>
> Du verkaufst etwas auf Kleinanzeigen, und viele Leute schreiben dir. Jede Nachricht kommt
> auch als E-Mail bei dir an. Dieses Programm liest diese E-Mails und macht daraus eine
> übersichtliche Seite: wer hat was gefragt, wer wartet noch auf Antwort, und wo ist Vorsicht
> geboten (zum Beispiel "zahle per PayPal, schreib mir auf WhatsApp"). Mit einem Klick landest
> du im richtigen Gespräch auf Kleinanzeigen und antwortest dort wie gewohnt.
>
> Das Programm meldet sich nie bei Kleinanzeigen an und schickt nichts ab. Dein Konto kann
> dadurch nicht gesperrt werden. Alles bleibt auf deinem Rechner.

**Deutsch** · [English](#english)

![Die Antwort-Seite mit erfundenen Beispiel-Nachrichten](docs/screenshot-desktop.png)
*Beispiel mit erfundenen Käufern. Gelb: Hinweise, auf die du achten solltest.*

## Was es macht

- Alle Gespräche auf einer Seite, nach Anzeige oder nach Käufer sortiert.
- Neue Nachrichten stehen oben und sind rot markiert.
- Warnhinweise: PayPal, Versand, Telefonnummer, Links, Preisangebot, gleicher Name in mehreren Gesprächen.
- Antwortvorlagen mit einem Klick ("Noch da?", "Kein Versand", "Schon weg").
- **Antwort senden** kopiert deinen Text und öffnet genau dieses Gespräch auf kleinanzeigen.de.
  Dort fügst du ihn ein und schickst ihn selbst ab.

## Warum es anders ist

Es gibt andere Werkzeuge für Kleinanzeigen. Die meisten melden sich mit deinem Konto an oder
steuern die Website. Dieses liest nur die Benachrichtigungs-E-Mails. Es braucht also kein Login,
birgt kein Risiko für dein Konto und berührt Kleinanzeigen nie.

## Installation

Du brauchst Python 3.11 oder neuer. Sonst nichts.

```bash
pip install git+https://github.com/capraCoder/kleinanzeigen-antworten
```

## Benutzung

**Aus gespeicherten Mails.** Exportiere die Kleinanzeigen-Mails als `.eml` oder `.mbox`
(z. B. aus Thunderbird oder Google Takeout). Dann:

```bash
ka-antworten ~/Downloads/kleinanzeigen.mbox --out antworten.html
```

Öffne `antworten.html` im Browser.

**Direkt aus dem Postfach.** Kopiere `config.example.toml` nach `config.toml` und trage unter
`[imap]` Server und Benutzer ein. Das Passwort steht nie in der Datei: es kommt aus der
Umgebungsvariable `KA_IMAP_PASSWORD` oder wird abgefragt. Bei Gmail brauchst du ein App-Passwort.

```bash
ka-antworten --imap --config config.toml
```

Das Postfach wird nur lesend geöffnet. Keine Mail wird verändert, nicht einmal als "gelesen" markiert.

**Erst mal ausprobieren**, ohne eigene Mails:

```bash
python -m tests.fake && ka-antworten tests/demo.mbox --out demo.html
```

In `config.toml` stellst du auch Vorlagen, Anzeigennamen und einen Countdown (z. B. "Abholung endet") ein.

## Datenschutz

Die Seite enthält Namen und Nachrichten deiner Käufer. Teile sie nicht. Nachnamen werden
standardmäßig abgekürzt ("Anna B."). Die `.gitignore` schließt Seiten, `config.toml` und
Mail-Exporte aus.

Dieses Projekt ist nicht mit Kleinanzeigen verbunden. "Kleinanzeigen" ist eine Marke ihres Inhabers.
MIT-Lizenz.

---

## English

> **In short**
>
> You sell things on Kleinanzeigen, Germany's largest classifieds site, and many people message
> you. Each message also arrives as an e-mail. This program reads those e-mails and turns them
> into one tidy page: who asked what, who is still waiting, and where to be careful. One click
> takes you to the right conversation on Kleinanzeigen, where you reply as usual.
>
> It never logs in to Kleinanzeigen and never sends anything. Your account cannot be banned
> because of it. Everything stays on your computer.

What makes ours different is that it only reads the notification emails, so it needs no login,
takes no account risk and never touches Kleinanzeigen.

- Install: `pip install git+https://github.com/capraCoder/kleinanzeigen-antworten` (Python 3.11 or later, no other dependencies).
- From saved mail: `ka-antworten <.eml/.mbox files or folders> --out antworten.html`
- From your mailbox, read-only: `ka-antworten --imap --config config.toml`. The password comes from
  `KA_IMAP_PASSWORD` or a prompt, never from the file.
- Try it: `python -m tests.fake && ka-antworten tests/demo.mbox --out demo.html`
- Tests: `python -m unittest`

The page holds your buyers' names and messages, so do not share it. Not affiliated with
Kleinanzeigen. MIT licence.
