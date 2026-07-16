# J.A.R.V.I.S — Sprach-Interface

Ein futuristisches "Jarvis"-Interface wie in Iron Man: ein großer, leuchtender
Energie-Orb, mit dem du **sprechen** kannst und dem du dein **Ziel** mitteilst.
Der Orb reagiert live auf deine Stimme, zeigt das erkannte Ziel als Text an und
**bestätigt es per deutscher Sprachausgabe**.

Reines Frontend — keine KI-Anbindung, keine Installation, kein Build.

![Ein leuchtender, audio-reaktiver 3D-Orb im HUD-Design]

## Funktionen

- **3D-Orb** (Three.js + WebGL-Shader) mit organisch waberndem Plasma und Bloom-Glühen.
- **Audio-reaktiv:** Der Orb pulsiert stärker, je lauter du sprichst.
- **Spracherkennung** auf Deutsch (`de-DE`) — Ziele werden live transkribiert.
- **Sprachausgabe:** JARVIS bestätigt jedes Ziel („Ziel verstanden: …“).
- **HUD** im Sci-Fi-Stil: Uhr, Statuszeile, Live-Transkript, Liste erfasster Ziele.

## Nutzung

1. Datei `index.html` in **Google Chrome** oder **Microsoft Edge** öffnen
   (Doppelklick genügt).
2. Beim ersten Klick den **Mikrofonzugriff erlauben**.
3. Auf den **Orb** oder den **Mikrofon-Button** klicken → Status wechselt zu
   „Ich höre zu …“.
4. Dein Ziel auf Deutsch sprechen. Es erscheint als Text, wird gespeichert und
   von JARVIS bestätigt.
5. Erneut klicken, um das Zuhören zu stoppen.

### Alternativ über einen lokalen Server

Manche Browser erlauben Mikrofon/Sprache nur über `http(s)`/`localhost`:

```bash
python3 -m http.server 8000
# dann im Browser öffnen:
# http://localhost:8000
```

## Hinweise

- **Browser:** Die Spracherkennung (Web Speech API) läuft zuverlässig in
  **Chrome/Edge**. In Firefox/Safari wird der Orb angezeigt, die Erkennung ist
  dort aber nicht vollständig verfügbar — ein Hinweis wird eingeblendet.
- **Internet:** Three.js wird beim ersten Öffnen per CDN geladen — eine
  Internetverbindung ist dafür nötig.
- **Datenschutz:** Alles läuft lokal im Browser. Die Spracherkennung nutzt die
  browsereigene Web Speech API; es wird nichts an eigene Server gesendet.

## Später eine echte KI anbinden

Die Stelle zum Andocken ist in `index.html` die `onresult`-Verarbeitung: dort
wird `goal` erkannt. Statt nur `speak('Ziel verstanden: ' + goal)` könntest du
`goal` an eine API (z. B. die Claude API) schicken und die Antwort mit `speak()`
ausgeben.
