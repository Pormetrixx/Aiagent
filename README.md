# AI Cold Calling Agent

Ein KI-gestützter Agent für automatisierte Kaltakquise-Telefonate mit Emotionserkennung und kontinuierlichem Training.

## 🎯 Projektziel

Entwicklung eines fortschrittlichen KI-Agenten für Kaltakquise-Telefonate, der:
- Kostenfrei auf einem Ubuntu 22 Server läuft
- Leads und Termine generiert
- Sich kontinuierlich durch Trainingsdaten verbessert
- Emotionales Gesprächsverhalten erkennt und adaptiert

## 🔑 Hauptfunktionen

- **Speech-to-Text**: Lokale Spracherkennung mit Whisper
- **Text-to-Speech**: Lokale Sprachsynthese mit Coqui TTS oder Mimic3
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

## 📂 Projektstruktur

```
├── config/               # Konfigurationsdateien
├── src/                 # Quellcode
│   ├── database/       # Datenbankoperationen
│   ├── speech/         # STT & TTS Module
│   ├── conversation/   # Gesprächssteuerung
│   └── training/       # Trainingsmodule
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

1. Kopieren Sie `config/config.example.yaml` nach `config/config.yaml`
2. Passen Sie die Konfigurationswerte an:
   - Datenbank-Verbindung
   - Modell-Pfade
   - Gesprächseinstellungen

## 🤝 Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Issue oder Pull Request.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.
