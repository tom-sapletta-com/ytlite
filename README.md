# YTLite - Minimalistyczny Pipeline YouTube 🎬

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

- **Markdown → Video** w 30 sekund
- **Auto-Shorts** (60s highlights) 
- **Free TTS** (edge-tts, wiele głosów)
- **Proste slajdy** (bez skomplikowanych animacji)
- **Auto-upload** do YouTube
- **Dzienny scheduler** (ustaw i zapomnij)
- **Docker support** (zero instalacji)

## Format contentu

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

## Codzienny workflow

```bash
# Rano: napisz jedną myśl (2 min)
nano content/episodes/dzisiaj.md

# Wygeneruj video (30 sekund)
make generate

# Wgraj automatycznie
make upload

# Gotowe! 
```

## Docker

```bash
# Zbuduj i uruchom
make docker-run

# Automatyzacja
make automation

# Preview
make preview  # http://localhost:8080
```

## Konfiguracja

1. **YouTube API:**
   - Idź do [Google Cloud Console](https://console.cloud.google.com/)
   - Włącz YouTube Data API v3
   - Pobierz `credentials.json` → `credentials/`

2. **Środowisko:**
   ```bash
   cp .env.example .env
   # Wypełnij swoje dane
   ```

3. **Głosy TTS:**
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

| Komenda | Opis |
|---------|------|
| `make help` | Pokaż wszystkie komendy |
| `make generate` | Wygeneruj filmy z markdown |
| `make shorts` | Stwórz Shorts z istniejących filmów |
| `make upload` | Wgraj na YouTube |
| `make publish` | Pełen pipeline (bez upload) |
| `make daily` | Generuj daily content |
| `make preview` | Preview na localhost:8080 |
| `make clean` | Wyczyść pliki |

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
- Docker (opcjonalne)

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
