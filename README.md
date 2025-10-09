# AI Cold Calling Agent

Ein KI-gestützter Agent für automatisierte Kaltakquise-Telefonate mit Emotionserkennung und kontinuierlichem Training.

## 🎯 Projektziel

Entwicklung eines fortschrittlichen KI-Agenten für Kaltakquise-Telefonate, der:
- Kostenfrei auf einem Ubuntu 22 Server läuft
- Leads und Termine generiert
- Sich kontinuierlich durch Trainingsdaten verbessert
- Emotionales Gesprächsverhalten erkennt und adaptiert
- **Flexible Auswahl zwischen lokalen und Cloud-basierten Sprach-APIs**

## 🔑 Hauptfunktionen

### Flexible Speech-to-Text (STT) Engines
Der Agent unterstützt mehrere STT-Engines, die per .env-Datei konfiguriert werden können:

- **Whisper** (OpenAI) - Lokal, kostenlos, GPU-beschleunigt
- **Deepgram** - Cloud API, Nova-2-Modell, hervorragende Qualität für Deutsch
- **Azure Speech Services** - Enterprise-grade, zuverlässig
- **Google Cloud Speech** - Hochwertige Transkription mit niedrigen Latenzen

### Flexible Text-to-Speech (TTS) Engines
Wählen Sie die optimale TTS-Engine für Ihre Anforderungen:

- **Coqui TTS** - Lokal, kostenlos, anpassbare Modelle
- **Mimic3** - Lokal, schnell, gute Qualität
- **ElevenLabs** - Premium API, extrem natürliche Stimmen
- **Azure Speech Services** - Professionelle Neural-Voices
- **Google Cloud TTS** - WaveNet und Neural2 Stimmen

### Weitere Funktionen
- **Telefonintegration**: Asterisk PBX Integration für professionelle Anrufverwaltung
- **Dialogsteuerung**: State-Machine + optionales lokales LLM (z.B. Ollama mit LLaMA-3, Mixtral)
- **Emotionserkennung**: Analyse und Anpassung des Gesprächsstils
- **Datenbank**: SQL-basierte Speicherung von:
  - Gesprächsleitfäden
  - FAQ und Antworten
  - Trainingsdaten
- **Dynamische Antwortgenerierung**: KI-gestützte Antworten bei fehlenden Datenbankeinträgen

## 🛠 Technische Anforderungen

- Ubuntu Server 22.04 LTS
- Python 3.8+
- PostgreSQL/MySQL für Datenspeicherung
- Asterisk PBX für Telefonintegration (optional)
- Ausreichend Speicherplatz für Modelle und Trainingsdaten
- Optional: GPU für bessere Performance bei lokalen Modellen

## 📂 Projektstruktur

```
├── config/               # Konfigurationsdateien
├── src/                 # Quellcode
│   ├── database/       # Datenbankoperationen
│   ├── speech/         # STT & TTS Module
│   │   ├── base.py              # Basis-Klassen für Engines
│   │   ├── stt.py               # Whisper STT
│   │   ├── stt_deepgram.py      # Deepgram STT
│   │   ├── stt_azure.py         # Azure STT
│   │   ├── stt_google.py        # Google Cloud STT
│   │   ├── tts.py               # Coqui & Mimic3 TTS
│   │   ├── tts_elevenlabs.py    # ElevenLabs TTS
│   │   ├── tts_azure.py         # Azure TTS
│   │   └── tts_google.py        # Google Cloud TTS
│   ├── conversation/   # Gesprächssteuerung
│   └── training/       # Trainingsmodule
├── docs/                # Dokumentation
│   ├── GERMAN_CALL_SCRIPTS.md  # Deutsche Gesprächsskripte
│   └── API.md                   # API-Dokumentation
├── tests/               # Tests
│   └── test_voice_engines.py   # Voice-Engine Tests
├── sql/                # SQL Schemas
└── requirements.txt    # Projektabhängigkeiten
```

## 🚀 Installation

```bash
# Repository klonen
git clone https://github.com/Pormetrixx/Aiagent.git
cd Aiagent

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
.\venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## 📝 Konfiguration

### Konfigurationsmethoden

Das System unterstützt **zwei Konfigurationsmethoden**:

#### Option 1: Nur .env-Datei (Empfohlen für einfache Setups)

Die einfachste Methode ist die Verwendung nur der `.env`-Datei:

```bash
# .env-Datei aus Vorlage erstellen
cp .env.example .env

# .env-Datei bearbeiten und API-Schlüssel eintragen
nano .env
```

**Das System funktioniert vollständig mit nur der .env-Datei.** Die `config.yaml` ist optional!

#### Option 2: .env + config.yaml (Erweiterte Konfiguration)

Für komplexere Setups können Sie zusätzlich `config.yaml` verwenden:

```bash
# config.yaml aus Vorlage erstellen (optional)
cp config/config.example.yaml config/config.yaml

# Erweiterte Einstellungen bearbeiten
nano config/config.yaml
```

Die `.env`-Werte überschreiben immer die `config.yaml`-Werte.

### 1. Umgebungsvariablen einrichten

```bash
# .env-Datei aus Vorlage erstellen
cp .env.example .env

# .env-Datei bearbeiten und API-Schlüssel eintragen
nano .env
```

### 2. Speech-to-Text Engine auswählen

In `.env`:
```bash
# Wählen Sie eine Engine: whisper, deepgram, azure, google
STT_ENGINE=whisper
STT_LANGUAGE=de

# Für Whisper (lokal, kostenlos)
STT_WHISPER_MODEL_SIZE=base
STT_WHISPER_DEVICE=cpu

# Für Deepgram (API, sehr gut für Deutsch)
DEEPGRAM_API_KEY=ihr_deepgram_api_key
STT_DEEPGRAM_MODEL=nova-2

# Für Azure Speech
AZURE_SPEECH_KEY=ihr_azure_key
AZURE_SPEECH_REGION=westeurope

# Für Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/pfad/zu/credentials.json
```

### 3. Text-to-Speech Engine auswählen

In `.env`:
```bash
# Wählen Sie eine Engine: coqui, mimic3, elevenlabs, azure, google
TTS_ENGINE=coqui
TTS_LANGUAGE=de

# Für Coqui TTS (lokal, kostenlos)
TTS_COQUI_MODEL=tts_models/de/thorsten/tacotron2-DDC
TTS_COQUI_DEVICE=cpu

# Für ElevenLabs (Premium-Qualität)
ELEVENLABS_API_KEY=ihr_elevenlabs_key
TTS_ELEVENLABS_VOICE_ID=voice_id_für_deutsche_stimme

# Für Azure TTS (professionell)
TTS_AZURE_VOICE=de-DE-KatjaNeural

# Für Google Cloud TTS
TTS_GOOGLE_VOICE=de-DE-Wavenet-C
```

**Hinweis:** Sie benötigen **keine** `config.yaml` Datei! Alle Einstellungen können über die `.env`-Datei vorgenommen werden. Das System verwendet Standardwerte für nicht gesetzte Optionen.

### 4. Empfohlene Stimmen für Investment Cold Calling (Deutsch)

#### Lokale Engines (kostenlos):
- **Coqui TTS**: `thorsten` (männlich, professionell)
- **Mimic3**: `de_DE/thorsten_low` (männlich, klar)

#### Cloud Engines (professionell):
- **Azure**: 
  - `de-DE-KatjaNeural` (weiblich, freundlich)
  - `de-DE-ConradNeural` (männlich, autoritativ)
- **Google Cloud**:
  - `de-DE-Wavenet-C` (weiblich, natürlich)
  - `de-DE-Neural2-B` (männlich, professionell)
- **ElevenLabs**: Custom Voice Cloning empfohlen für Markenkonsistenz

### 5. Konfigurationsdatei anpassen (optional)

Für erweiterte Einstellungen:
```bash
# config.yaml aus Vorlage erstellen
cp config/config.example.yaml config/config.yaml

# Konfiguration bearbeiten
nano config/config.yaml
```

## 🧪 Testen der Voice Engines

Führen Sie das Test-Script aus, um alle konfigurierten Engines zu überprüfen:

```bash
python tests/test_voice_engines.py
```

Das Script:
- Überprüft die Verfügbarkeit aller Engines
- Testet STT mit Beispiel-Audio (falls vorhanden)
- Testet TTS und erstellt Audio-Samples
- Zeigt eine Zusammenfassung aller Tests

## 🎤 Gesprächsskripte

Deutsche Gesprächsskripte für Investment Lead Generation finden Sie in:
`docs/GERMAN_CALL_SCRIPTS.md`

Diese beinhalten:
- Eröffnungsszenarien
- Qualifizierungsfragen
- Einwandbehandlung
- Nutzenargumentation
- Abschluss-Techniken
- Voicemail-Skripte

## 💡 API-Schlüssel und Credits

### Kostenlose/Lokale Optionen:
- **Whisper**: Vollständig kostenlos, läuft lokal
- **Coqui TTS**: Vollständig kostenlos, läuft lokal
- **Mimic3**: Vollständig kostenlos, läuft auf lokalem Server

### Cloud APIs mit kostenlosen Kontingenten:
- **Deepgram**: $200 Free Credits, dann $0.0043/Minute
- **Azure Speech**: 5 Std/Monat gratis, dann ab €0.84/Std
- **Google Cloud**: $300 Credits für neue Konten, dann ab $0.006/15 Sek

### Premium APIs:
- **ElevenLabs**: Ab $5/Monat für 30.000 Zeichen

## 🔐 API-Schlüssel erhalten

### Deepgram:
1. Registrieren auf https://console.deepgram.com/
2. API-Schlüssel erstellen
3. Nova-2 Model für beste deutsche Spracherkennung verwenden

### Azure Speech Services:
1. Azure-Konto erstellen: https://portal.azure.com/
2. "Speech Services" Ressource erstellen
3. API-Schlüssel und Region kopieren

### Google Cloud:
1. GCP-Konto erstellen: https://console.cloud.google.com/
2. "Speech-to-Text" und "Text-to-Speech" APIs aktivieren
3. Service-Account erstellen und JSON-Credentials herunterladen

### ElevenLabs:
1. Registrieren auf https://elevenlabs.io/
2. API-Schlüssel im Dashboard generieren
3. Deutsche Stimmen auswählen oder Voice Cloning nutzen

## 🏃 System starten

```bash
# Agent starten
python3 run.py start

# Mit custom config
python3 run.py start -c /pfad/zu/config.yaml

# Als Systemdienst (nach setup.sh)
sudo systemctl start aiagent
```

## 📊 Performance-Empfehlungen

### Für optimale Latenz:
- **STT**: Deepgram Nova-2 (schnellste Cloud-Lösung)
- **TTS**: Azure Neural Voices (niedrige Latenz)

### Für beste Qualität:
- **STT**: Google Cloud (höchste Genauigkeit)
- **TTS**: ElevenLabs (natürlichste Stimmen)

### Für Kosteneffizienz:
- **STT**: Whisper lokal (mit GPU für gute Performance)
- **TTS**: Coqui TTS lokal

### Für Datenschutz (On-Premise):
- **STT**: Whisper lokal
- **TTS**: Coqui TTS oder Mimic3 lokal

## 🔧 Troubleshooting

Siehe `SETUP.md` für detaillierte Installationsanweisungen und Fehlerbehebung.

### Häufige Probleme:

1. **Engine nicht verfügbar**: API-Schlüssel überprüfen
2. **Schlechte Audio-Qualität**: Sample-Rate und Codec prüfen
3. **Hohe Latenz**: Netzwerkverbindung oder lokale Engine nutzen
4. **API-Limits erreicht**: Zu kostenlosem Tier oder lokalem Model wechseln

## 🤝 Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Issue oder Pull Request.

### Neue Engines hinzufügen:

1. Erstellen Sie eine neue Engine-Klasse (erbt von `BaseSTTEngine` oder `BaseTTSEngine`)
2. Implementieren Sie die erforderlichen Methoden
3. Fügen Sie die Engine zur Factory-Funktion hinzu
4. Aktualisieren Sie `.env.example` und Dokumentation
5. Fügen Sie Tests hinzu

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 🌟 Features Roadmap

- [ ] OpenAI Whisper API Integration
- [ ] OpenVoice TTS Integration
- [ ] Streaming-Audio-Support für alle Engines
- [ ] Automatic Engine Fallback bei Ausfällen
- [ ] Voice Activity Detection (VAD) Integration
- [ ] Multi-Language Support über alle Engines
- [ ] Performance Benchmarks für alle Engines
