# YTLite - Minimalistyczny Pipeline YouTube 🎬

[![PyPI version](https://badge.fury.io/py/ytlite.svg)](https://badge.fury.io/py/ytlite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Filozofia:** Simple > Complex, Consistency > Perfection

Stwórz filmy YouTube z markdown w 30 sekund. Automatyzacja, która nie przeszkadza w kreatywności.

## Quick Start

```bash
# 1. Sklonuj i zainstaluj
git clone https://github.com/tom-sapletta-com/ytlite
cd ytlite
make install

# 2. Skonfiguruj .env
cp .env.example .env
# Dodaj swoje klucze API

# 3. Stwórz pierwszy film
echo "Twoja genialna myśl" > content/episodes/first.md
make generate

# 4. Zobacz rezultat
make preview  # http://localhost:8080
```

## Główne funkcje

- **Markdown → Video** w 30 sekund → [`src/ytlite.py`](src/ytlite.py)
- **Auto-Shorts** (60s highlights) → [`create_shorts()`](src/ytlite.py#L180)
- **Free TTS** (edge-tts, wiele głosów) → [`generate_audio()`](src/ytlite.py#L120)
- **Proste slajdy** (bez skomplikowanych animacji) → [`create_slides()`](src/ytlite.py#L90)
- **Auto-upload** do YouTube → [`youtube_uploader.py`](src/youtube_uploader.py)
- **OAuth Desktop App** (bezpieczna autoryzacja) → [`tauri-youtube-oauth/`](tauri-youtube-oauth/)
- **Dzienny scheduler** (ustaw i zapomnij) → [`scheduler.py`](src/scheduler.py)
- **Docker support** (zero instalacji) → [`Dockerfile`](Dockerfile) + [`docker-compose.yml`](docker-compose.yml)

## Format contentu

Przykłady: [`content/episodes/`](content/episodes/)

```markdown
---
title: "Twój tytuł"
date: 2025-01-15
theme: tech  # lub: philosophy, wetware
tags: [ai, przyszłość, tech]
---

Pierwszy akapit staje się pierwszym slajdem.

Drugi akapit to drugi slajd.

Krótko. Konkretnie. Skutecznie.
```

### Przykładowe treści:
- [`welcome.md`](content/episodes/welcome.md) - wprowadzenie do YTLite
- [`wetware_intro.md`](content/episodes/wetware_intro.md) - temat wetware/cyborgizacji
- [`philosophy_time.md`](content/episodes/philosophy_time.md) - refleksje filozoficzne

## Codzienny workflow

```bash
# Rano: napisz jedną myśl (2 min)
nano content/episodes/dzisiaj.md

# Wygeneruj video (30 sekund)
make generate

# Wgraj automatycznie
make upload

# Preview
make preview  # http://localhost:8080
```

## Features

### 🎬 Content Creation
- **Single-File SVG Projects**: Each project stored as one SVG file with embedded metadata and media
- **DataURI Media Embedding**: MP4, MP3, WAV files embedded directly in SVG using data URIs
- **Interactive SVG Files**: SVG files playable in browsers with video controls and metadata display
- **Thumbnail Integration**: SVG serves as both project container and video thumbnail
- **Multi-language Support**: Generate content in multiple languages with locale-specific voices
- **Voice Synthesis**: High-quality text-to-speech using Azure Cognitive Services with 200+ voices

### 🔧 Advanced Validation & Management
- **XML Validation**: Comprehensive SVG validation with automatic error fixing
- **Version Control**: Automatic backup system for all project modifications
- **Project Management**: Complete lifecycle management via Web GUI
- **Batch Operations**: Bulk validation and processing of multiple projects

### 🌐 Integrations & Publishing
- **WordPress Integration**: Direct publishing to WordPress sites with embedded SVG media
- **Docker WordPress**: Containerized WordPress environment for testing and development
- **Nextcloud Integration**: Content synchronization and remote storage for SVG projects
- **Web GUI**: Modern, responsive web interface with SVG project browser
- **REST API**: Complete programmatic access to all functionality

### 🛡️ Security & Performance
- **Path Traversal Protection**: Secure file access with validation
- **Input Sanitization**: Comprehensive validation of all user inputs
- **Performance Optimization**: Efficient processing with progress tracking
- **Error Recovery**: Graceful handling of failures with detailed logging

## Nowy Web GUI (Zarządzanie Projektami)

Nowy, rozbudowany interfejs webowy do zarządzania projektami, edycji, walidacji i publikacji.

### Uruchomienie

```bash
# Uruchom serwer deweloperski GUI
python3 run_new_gui.py
```

- Otwórz w przeglądarce: **http://localhost:5000**

### Funkcje

- **Zarządzanie projektami**: Przeglądanie, tworzenie i usuwanie projektów w widoku siatki lub tabeli.
- **Edytor w czasie rzeczywistym**: Edytuj pliki markdown i metadane z podglądem na żywo.
- **Walidacja**: Uruchamiaj walidację projektu bezpośrednio z interfejsu.
- **Publikacja**: Publikuj filmy na YouTube i posty na WordPress jednym kliknięciem.
- **Podgląd mediów**: Zobacz wygenerowane wideo, audio i miniatury.

Powiązania z podglądem NGINX:
- Równolegle możesz uruchomić `make preview` (http://localhost:8080) do przeglądania całego `output/`.
- Jeśli ustawisz `PUBLIC_BASE_URL` (np. `http://localhost:8080`), linki w postach WordPress będą absolutne.

### Publikacja na WordPress przez GUI
Wymagane zmienne w `.env` (per‑project lub globalnie):
- `WORDPRESS_URL` — np. `https://twoj‑wordpress.pl`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD` — Application Password użytkownika WP
- (opcjonalnie) `PUBLIC_BASE_URL` — np. `http://localhost:8080`

GUI umieszcza miniaturę w Media Library i tworzy post z treścią z `description.md`, linkami do audio i osadzonym wideo.

### Integracja z Nextcloud (WebDAV)
W GUI podaj ścieżkę zdalną (np. `/YT/content/materiał.md`) i kliknij „Fetch to content/episodes/”.
Zmienne w `.env` (per‑project lub globalnie):
- `NEXTCLOUD_URL`, `NEXTCLOUD_USERNAME`, `NEXTCLOUD_PASSWORD`

### Upload na YouTube — per projekt i per konto
- Cel Makefile: `make upload-project PROJECT=<nazwa> [PRIVACY=public|unlisted|private]`
- Mechanizm ładuje najpierw `output/projects/<nazwa>/.env`, a potem globalne `.env`.

## Per‑project `.env` (multi‑account)

Umieść w `output/projects/<projekt>/.env`. Ten plik ma pierwszeństwo przed globalnym `.env`.
Przykładowe klucze:

```env
# YouTube
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
UPLOAD_PRIVACY=unlisted

# WordPress
WORDPRESS_URL=https://twoj‑wordpress.pl
WORDPRESS_USERNAME=twoj_login
WORDPRESS_APP_PASSWORD=app‑password‑wp
PUBLIC_BASE_URL=http://localhost:8080

# Nextcloud
NEXTCLOUD_URL=https://cloud.example.com
NEXTCLOUD_USERNAME=...
NEXTCLOUD_PASSWORD=...

# Audio/Voice (opcjonalnie)
EDGE_TTS_VOICE=pl-PL-MarekNeural
```

CLI też obsługuje per‑project `.env` przy generacji (patrz `YTLite.generate_video()`), a GUI automatycznie ładuje `.env` wgrywany/znajdujący się w folderze projektu.

## Walidacje danych i aplikacji

- `make validate-app` — smoke test (zależności + szybka generacja + sprawdzenie pakietowania projektu)
  - Raporty per‑projekt: `app_validate.json`, `app_validate.md` (w `output/projects/<nazwa>/`)
- `make validate-data` — skanuje wszystkie projekty i tworzy raport integralności
  - Globalny: `output/validate_data.json`
  - Per‑projekt: `data_report.json`, `data_report.md`

## Praca z Dockerem 🐳

Docker to zalecany sposób uruchamiania projektu. Eliminuje problemy z zależnościami i zapewnia spójne środowisko.

### Główna Aplikacja (Generowanie Wideo)

1.  **Zbuduj obrazy** (tylko za pierwszym razem lub po zmianie zależności):
    ```bash
    make docker-build
    ```

2.  **Uruchom usługi** (aplikacja i serwer podglądu):
    ```bash
    make docker-up
    ```

3.  **Otwórz powłokę w kontenerze**, aby pracować z `make`:
    ```bash
    make docker-shell
    ```
    Wewnątrz kontenera możesz używać poleceń, tak jak lokalnie:
    ```bash
    # Będąc wewnątrz kontenera:
    make generate
    make upload
    ```

4.  **Zatrzymaj usługi**:
    ```bash
    make docker-down
    ```

### Web GUI w Docker Compose

Dodaliśmy usługę `webgui` (Flask) na porcie `5000`.

```bash
# Uruchom samą usługę GUI
docker-compose --profile gui up -d webgui

# Logi GUI
docker-compose logs -f webgui

# Przeglądarka
open http://localhost:5000
```

### Aplikacja Tauri (OAuth Helper)

1.  **Uruchom kontener deweloperski**:
    ```bash
    make tauri-dev
    ```

2.  **Otwórz powłokę w kontenerze Tauri**:
    ```bash
    make tauri-shell
    ```

3.  **Uruchom testy**:
    ```bash
    make tauri-test
    ```

## Konfiguracja

### 🔑 Pliki konfiguracyjne:
- [`.env.example`](.env.example) - zmienne środowiskowe (API keys, ustawienia)
- [`config.yaml`](config.yaml) - główna konfiguracja (głosy, motywy, jakość)
- [`Makefile`](Makefile) - komendy automatyzacji

### 1. **YouTube API:**
   - Idź do [Google Cloud Console](https://console.cloud.google.com/)
   - Włącz YouTube Data API v3
   - Pobierz `credentials.json` → `credentials/`

### 2. **Środowisko:**
   ```bash
   cp .env.example .env
   # Wypełnij swoje dane
   ```

### 3. **Głosy TTS:**
   ```yaml
   # config.yaml
   voice: pl-PL-MarekNeural  # Mężczyzna PL
   # voice: pl-PL-ZofiaNeural  # Kobieta PL
   # voice: en-US-AriaNeural   # Kobieta EN
```

## Motywy

1. **tech** - ciemny z niebieskimi akcentami
2. **philosophy** - minimalistyczny ze złotymi akcentami  
3. **wetware** - fioletowy gradient, futurystyczny

## Automatyzacja

```bash
# Codzienne generowanie
make automation

# Lub jednorazowo
make daily
```

## Statystyki

```bash
make stats
```

## Komendy

| Komenda | Opis | Kod |
|---------|------|-----|
| `make help` | Pokaż wszystkie komendy | [Makefile:9](Makefile#L9) |
| `make generate` | Wygeneruj filmy z markdown | [Makefile:17](Makefile#L17) |
| `make shorts` | Stwórz Shorts z istniejących filmów | [Makefile:25](Makefile#L25) |
| `make upload` | Wgraj na YouTube | [Makefile:30](Makefile#L30) |
| `make publish` | Pełny pipeline (bez upload) | [Makefile:35](Makefile#L35) |
| `make daily` | Generuj daily content | [Makefile:40](Makefile#L40) |
| `make preview` | Preview na localhost:8080 | [Makefile:70](Makefile#L70) |
| `make clean` | Wyczyść pliki | [Makefile:100](Makefile#L100) |
| `make docker-tts` | Uruchom usługę TTS | [Makefile:85](Makefile#L85) |
| `make docker-video` | Uruchom usługę generowania wideo | [Makefile:90](Makefile#L90) |
| `make docker-upload` | Uruchom usługę uploadu na YouTube | [Makefile:95](Makefile#L95) |
| `make docker-all-services` | Uruchom wszystkie wyspecjalizowane usługi | [Makefile:100](Makefile#L100) |

## Dlaczego YTLite?

- **80% mniej złożoności** niż profesjonalne narzędzia
- **100% automatyzacji** możliwe
- **0$ koszt** (wszystkie darmowe narzędzia)
- **Konsystentność > sporadyczna perfekcja**

## Filozofia

> "Najlepszy content to opublikowany content, nie perfekcyjny content."

Skup się na **pomysłach**, nie na produkcji. Niech roboty zajmują się resztą.

---

## Przykłady użycia

### Quick content z stdin
```bash
echo "Dziś myślę o AI..." | make quick
```

### Batch processing
```bash
make generate  # Wszystkie pliki z content/episodes/
```

### Watch mode
```bash
make dev-watch  # Auto-generuj przy zmianie plików
```

## Wymagania

- Python 3.9+
- FFmpeg
- Docker (opcjonalnie)

## Instalacja

### Automatyczna
```bash
curl -sSL https://raw.githubusercontent.com/tom-sapletta-com/ytlite/main/install.sh | bash
```

### Manualna
```bash
git clone https://github.com/tom-sapletta-com/ytlite
cd ytlite
pip install -r requirements.txt
make install
```

## Wsparcie

- GitHub Issues: [github.com/tom-sapletta-com/ytlite](https://github.com/tom-sapletta-com/ytlite)
- Blog: [wetware.dev](https://wetware.dev)

---

*YTLite - Bo życie jest za krótkie na ręczny montaż* 
