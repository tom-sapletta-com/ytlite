# YTLite - Dokumentacja Techniczna 📖

## 🏗️ Architektura Systemu

### Core Modules

#### [`src/ytlite.py`](src/ytlite.py) - Główny Generator
**Klasy i funkcje:**
- `YTLite` (linia ~50) - główna klasa generatora
- `generate_video()` (linia ~80) - generuje video z markdown
- `create_slides()` (linia ~120) - tworzy slajdy z tekstem
- `generate_audio()` (linia ~160) - TTS audio generation
- `create_shorts()` (linia ~200) - generuje YouTube Shorts
- `generate_thumbnail()` (linia ~240) - tworzy miniaturki

#### [`src/youtube_uploader.py`](src/youtube_uploader.py) - Upload Manager
**Klasy i funkcje:**
- `YouTubeUploader` (linia ~30) - główna klasa uploadu
- `authenticate()` (linia ~50) - OAuth2 authentication
- `upload_video()` (linia ~100) - upload pojedynczego video
- `upload_shorts()` (linia ~150) - upload shorts z #Shorts tag
- `batch_upload()` (linia ~200) - upload wielu plików

#### [`src/scheduler.py`](src/scheduler.py) - Automatyzacja
**Klasy i funkcje:**
- `ContentScheduler` (linia ~25) - scheduler główny
- `generate_daily_content()` (linia ~60) - dzienna generacja
- `pick_random_topic()` (linia ~90) - losowy wybór tematu
- `run_scheduler()` (linia ~120) - uruchomienie schedulera

## 📁 Kluczowe Pliki Konfiguracyjne

### [`config.yaml`](config.yaml) - Główna Konfiguracja 
```yaml
# Głosy TTS
voice: pl-PL-MarekNeural

# Ustawienia video
resolution: 1920x1080
fps: 30
font_size: 48

# Motywy kolorystyczne
themes:
  tech: "#1a1a2e"      # ciemny niebieski
  philosophy: "#2c1810"  # ciepły brąz
  wetware: "#1a0633"     # fioletowy
```

### [`.env.example`](.env.example) - Zmienne Środowiskowe
```bash
# YouTube API (wymagane)
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_CHANNEL_ID=your_channel_id

# TTS Settings
EDGE_TTS_VOICE=pl-PL-MarekNeural

# Automation
AUTO_UPLOAD=false
SCHEDULE_TIME=09:00
```

### [`Makefile`](Makefile) - Komendy Automatyzacji
**Najważniejsze komendy:**
- `make generate` (linia 17) - generuj wszystkie filmy
- `make shorts` (linia 25) - twórz shorts
- `make upload` (linia 30) - wgraj na YouTube
- `make daily` (linia 40) - pełen dzienny pipeline
- `make automation` (linia 50) - uruchom scheduler

## 🐳 Docker Configuration

### [`Dockerfile`](Dockerfile)
```dockerfile
FROM python:3.11-slim
# System dependencies: ffmpeg, sox, espeak-ng
RUN apt-get update && apt-get install -y ffmpeg sox espeak-ng
# Python environment setup
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### [`docker-compose.yml`](docker-compose.yml)
**Services:**
- `ytlite` - główny generator (port mapping, volume mounts)
- `nginx` - preview server (localhost:8080)
- `scheduler` - automated daily generation

## 📝 Content Format

### Struktura Markdown ([`content/episodes/`](content/episodes/))

```markdown
---
title: "Tytuł odcinka"           # wymagane
date: 2025-01-15                 # wymagane  
theme: tech                      # tech|philosophy|wetware
tags: [ai, automation]           # opcjonalne
duration: auto                   # opcjonalne
---

Pierwszy paragraf = pierwszy slajd.

Drugi paragraf = drugi slajd.

Każdy paragraf to osobny slajd w video.
```

**Przykłady:**
- [`welcome.md`](content/episodes/welcome.md) - podstawowy przykład
- [`wetware_intro.md`](content/episodes/wetware_intro.md) - temat cyborgizacji
- [`philosophy_time.md`](content/episodes/philosophy_time.md) - refleksje

## 🔧 Workflow Techniczny

### 1. Content → Video Pipeline
```
markdown → frontmatter parsing → text splitting → 
TTS audio → slide generation → video composition → 
shorts extraction → thumbnail creation
```

### 2. Upload Pipeline  
```
video files → YouTube API authentication → 
metadata preparation → upload → shorts processing → 
upload history tracking
```

### 3. Automation Pipeline
```
scheduler start → topic selection → content generation → 
video creation → optional upload → logging
```

## 🛠️ Development Setup

```bash
# 1. Środowisko developerskie
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Testowanie modułów
python3 -m pytest src/
python3 src/ytlite.py --help

# 3. Development z watch mode
make dev-watch  # auto-regeneracja przy zmianach
```

## 📊 Output Structure

```
output/
├── videos/           # Główne filmy MP4
│   ├── welcome_2025-01-15.mp4
│   └── ...
├── shorts/           # YouTube Shorts (9:16)
│   ├── welcome_2025-01-15_short.mp4  
│   └── ...
├── thumbnails/       # Miniaturki PNG
│   ├── welcome_2025-01-15.png
│   └── ...
└── audio/           # Pliki TTS (cache)
    ├── welcome_audio.wav
    └── ...
```

## 🚀 Production Deployment

### Option 1: Docker (Recommended)
```bash
make docker-build
make docker-run
make automation  # uruchom scheduler
```

### Option 2: Systemd Service
```bash
# Zainstaluj jako service
sudo cp ytlite.service /etc/systemd/system/
sudo systemctl enable ytlite
sudo systemctl start ytlite
```

## 🐛 Troubleshooting

### Częste problemy:

1. **TTS Error**: Sprawdź połączenie internetowe
2. **Upload Failed**: Zweryfikuj YouTube API credentials  
3. **Video Generation Error**: Sprawdź FFmpeg installation
4. **Permission Denied**: `chmod +x install.sh`

### Debug mode:
```bash
export DEBUG=1
make generate  # verbose output
```

### Logi:
```bash
tail -f logs/ytlite.log      # główne logi
tail -f logs/scheduler.log   # logi schedulera  
tail -f logs/upload.log      # logi uploadu
```
