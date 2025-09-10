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
