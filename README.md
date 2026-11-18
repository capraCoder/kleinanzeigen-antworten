# kleinanzeigen-antworten

> **Kurz erklärt**
>
> Du verkaufst etwas auf Kleinanzeigen, und viele Leute schreiben Dir. Jede Nachricht kommt
> auch als E-Mail bei Dir an. Dieses Programm liest diese E-Mails und macht daraus eine
> übersichtliche Seite: wer hat was gefragt, wer wartet noch auf Antwort, und wo ist Vorsicht
> geboten (zum Beispiel "zahle per PayPal, schreib mir auf WhatsApp"). Mit einem Klick landest
> Du im richtigen Gespräch auf Kleinanzeigen und antwortest dort wie gewohnt.
>
> Das Programm meldet sich nie bei Kleinanzeigen an und schickt nichts ab. Dein Konto kann
> dadurch nicht gesperrt werden. Alles bleibt auf Deinem Rechner.

**Deutsch** · [English](#english)

![Die Antwort-Seite mit erfundenen Beispiel-Nachrichten](docs/screenshot-desktop.png)
*Beispiel mit erfundenen Käufern. Gelb: Hinweise, auf die Du achten solltest.*

## Was es macht

- Alle Gespräche auf einer Seite, nach Anzeige oder nach Käufer sortiert.
- Neue Nachrichten stehen oben und sind rot markiert.
- Warnhinweise: PayPal, Versand, Telefonnummer, Links, Preisangebot, gleicher Name in mehreren Gesprächen.
- Antwortvorlagen mit einem Klick ("Noch da?", "Kein Versand", "Schon weg").
- **Antwort senden** kopiert Deinen Text und öffnet genau dieses Gespräch auf kleinanzeigen.de.
  Dort fügst Du ihn ein und schickst ihn selbst ab.

## Warum es anders ist

Es gibt andere Werkzeuge für Kleinanzeigen. Die meisten melden sich mit Deinem Konto an oder
steuern die Website. Dieses *liest* nur die Benachrichtigungs-E-Mails: entweder legst Du sie selbst in einen Ordner,
oder es holt sie automatisch aus Deinem Postfach (IMAP, nur lesend). Es braucht also kein Login,
birgt kein Risiko für Dein Konto und berührt Kleinanzeigen nie.

## So geht's (einfach)

### Teil 1: Einmal einrichten

*Nur beim ersten Mal, etwa 10 Minuten.*

1. **Python installieren.** Lade es von [python.org/downloads](https://www.python.org/downloads/)
   herunter. Unter Windows beim Installieren das Häkchen **"Add python.exe to PATH"** setzen.
2. **Programm installieren.** Öffne die Eingabeaufforderung (Windows-Taste, "cmd" tippen, Enter)
   oder unter macOS das "Terminal". Kopiere diese Zeile hinein und drücke Enter:

   ```
   pip install git+https://github.com/capraCoder/kleinanzeigen-antworten
   ```

### Teil 2: Neue Nachrichten holen

*Jedes Mal, wenn neue Kleinanzeigen-Mails da sind.*

1. **Mails in einen Ordner legen.** Lege auf dem Schreibtisch einen Ordner `Kleinanzeigen` an.
   - *Thunderbird oder Outlook:* Kleinanzeigen-Mails markieren und mit der Maus in den Ordner ziehen.
   - *Gmail im Browser:* Mail öffnen, oben rechts auf ⋮ und **"Nachricht herunterladen"**, dann in den Ordner legen.
2. **Seite bauen.** In der Eingabeaufforderung:

   ```
   cd Desktop
   ka-antworten Kleinanzeigen
   ```

3. **Seite öffnen.** Auf dem Schreibtisch liegt jetzt `antworten.html`. Doppelklick, fertig.

Nur mal schauen, wie es aussieht? Das Bild oben zeigt es mit erfundenen Käufern.

## Für Fortgeschrittene

<details>
<summary>Postfach direkt lesen, Vorlagen, Demo, Tests</summary>

**Direkt aus dem Postfach (IMAP, nur lesend).** `config.example.toml` nach `config.toml` kopieren,
unter `[imap]` Server und Benutzer eintragen. Das Passwort steht nie in der Datei: es kommt aus
`KA_IMAP_PASSWORD` oder wird abgefragt. Gmail braucht ein App-Passwort. Der Ordner wird mit
`readonly` und `BODY.PEEK` geöffnet: keine Mail wird verändert, nicht einmal als gelesen markiert.

```bash
ka-antworten --imap --config config.toml
```

**Eingaben:** `.eml`, `.mbox` (Thunderbird, Google Takeout) oder Ordner davon; `--out` wählt die Ausgabedatei.

**Einstellungen** in `config.toml`: Titel, volle Namen, Anzeigennamen, Antwortvorlagen, Countdown mit Phasen.

**Anzeigen-Vorschau.** Ein Klick auf einen Anzeigentitel (oder das Anzeigen-Kärtchen in der
Käufer-Ansicht) öffnet ein Fenster: alle Gespräche zu dieser Anzeige mit Sprung dorthin und die
letzte Nachricht. Mit `[ad_details."<Nr>"]` in `config.toml` kommen Preis, Anzeigentext, Link und
Fotos dazu. Fotos sind Dateien neben der Seite oder `https://`-Adressen, andere Links werden
verworfen.

**Demo und Tests** (im Quellordner):

```bash
python -m tests.fake && ka-antworten tests/demo.mbox --out demo.html
python -m unittest
```

</details>

## Datenschutz

Die Seite enthält Namen und Nachrichten Deiner Käufer. Teile sie nicht. Nachnamen werden
standardmäßig abgekürzt ("Anna B."). Die `.gitignore` schließt Seiten, `config.toml` und
Mail-Exporte aus.

Dieses Projekt ist nicht mit Kleinanzeigen verbunden. "Kleinanzeigen" ist eine Marke ihres Inhabers.

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

What makes ours different is that it only *reads* the notification emails (you drop them into a
folder, or it fetches them read-only from your mailbox over IMAP), so it needs no Kleinanzeigen
login, takes no account risk and never touches Kleinanzeigen.

- Install: `pip install git+https://github.com/capraCoder/kleinanzeigen-antworten` (Python 3.11 or later).
- From saved mail: `ka-antworten <.eml/.mbox files or folders> --out antworten.html`
- From your mailbox, read-only: `ka-antworten --imap --config config.toml`. The password comes from
  `KA_IMAP_PASSWORD` or a prompt, never from the file.
- Try it: `python -m tests.fake && ka-antworten tests/demo.mbox --out demo.html`
- Tests: `python -m unittest`

The page holds your buyers' names and messages, so do not share it. Not affiliated with
Kleinanzeigen.

---

## Lizenz / Licence

**Deutsch.** Frei nutzen, verändern, weitergeben und forken: ja. Damit Geld verdienen: nein.
Lizenz: [PolyForm Noncommercial 1.0.0](LICENSE). Wer es weitergibt oder darauf aufbaut, nennt bitte
die Quelle mit genau dieser Zeile (zum Kopieren):

```
Based on kleinanzeigen-antworten by capraCoder (https://github.com/capraCoder/kleinanzeigen-antworten)
```

**English.** Use, change, share and fork it freely: yes. Make money with it: no.
Licence: [PolyForm Noncommercial 1.0.0](LICENSE). If you share it or build on it, please credit it
with exactly this line (copy and paste):

```
Based on kleinanzeigen-antworten by capraCoder (https://github.com/capraCoder/kleinanzeigen-antworten)
```

---

## Haftungsausschluss / Disclaimer

**Deutsch.** Diese Software wird kostenlos und ohne jede Gewähr bereitgestellt ("wie besehen"),
siehe [LICENSE](LICENSE). Die Nutzung erfolgt auf eigenes Risiko. Für Schäden, Datenverlust,
entgangene Verkäufe oder Maßnahmen Dritter (z. B. Kontosperrungen) wird keine Haftung übernommen,
soweit gesetzlich zulässig. Du bist selbst verantwortlich für die Einhaltung der Nutzungsbedingungen
von Kleinanzeigen und Deines E-Mail-Anbieters sowie des Datenschutzrechts (DSGVO) beim Umgang mit
den Daten Deiner Käufer. Dieses Projekt ist kein offizielles Angebot von Kleinanzeigen und steht in
keiner Verbindung zu Kleinanzeigen; "Kleinanzeigen" ist eine Marke ihres Inhabers. Dies ist keine
Rechtsberatung.

**English.** This software is provided free of charge and "as is", without warranty of any kind;
see [LICENSE](LICENSE). You use it at your own risk. To the extent permitted by law, no liability is
accepted for damage, data loss, lost sales or actions by third parties (such as account
restrictions). You are responsible for complying with the terms of Kleinanzeigen and of your e-mail
provider, and with data-protection law (GDPR) when handling your buyers' data. This project is not
an official Kleinanzeigen product and is not affiliated with Kleinanzeigen; "Kleinanzeigen" is a
trademark of its owner. This is not legal advice.
