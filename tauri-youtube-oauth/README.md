# Tauri YouTube OAuth 🔐

**Desktop OAuth app for YTLite YouTube integration**

Aplikacja desktop do bezpiecznej autoryzacji YouTube API bez konieczności hostowania serwera callback.

## 🎯 Cel

Tauri OAuth app rozwiązuje problem callbacku OAuth2 w YTLite:
- **Problem**: YouTube OAuth wymaga callback URL, ale YTLite to CLI tool
- **Rozwiązanie**: Desktop app z wbudowanym web serverem na `localhost:14321`
- **Bezpieczeństwo**: Tokeny przechowywane lokalnie, nie w chmurze

## 🏗️ Architektura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YTLite CLI    │    │  Tauri Desktop   │    │  YouTube API    │
│                 │────│     OAuth        │────│                 │
│ python uploader │    │ React + Rust     │    │  Google OAuth   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Struktura Projektu

```
tauri-youtube-oauth/
├── src/                    # 🎨 Frontend React
│   ├── App.tsx            # Główny komponent UI
│   ├── main.tsx           # Entry point React
│   └── oauth.ts           # OAuth client logic
├── src-tauri/             # 🦀 Backend Rust
│   ├── src/
│   │   └── main.rs        # Tauri commands + OAuth server
│   └── Cargo.toml         # Zależności Rust
├── package.json           # Zależności Node.js
├── tauri.conf.json        # Konfiguracja Tauri
└── README.md              # Ta dokumentacja
```

## ⚙️ Konfiguracja

### 1. Wymagania
```bash
# Zainstaluj Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Zainstaluj Tauri CLI
cargo install tauri-cli

# Zainstaluj Node dependencies  
npm install
```

### 2. Google Cloud Console
1. Idź do [Google Cloud Console](https://console.cloud.google.com/)
2. Utwórz nowy projekt lub wybierz istniejący
3. Włącz **YouTube Data API v3**
4. Idź do **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. **Application type**: Desktop application
6. **Authorized redirect URIs**: `http://127.0.0.1:14321/callback`

### 3. Uruchomienie
```bash
cd tauri-youtube-oauth

# Development mode
npm run dev

# Build production
npm run build
```

## 🚀 Workflow OAuth

### 1. Konfiguracja w aplikacji
```typescript
// Wklej Client ID i Client Secret z Google Console
const config = {
  client_id: "twoj_client_id.googleusercontent.com",
  client_secret: "twoj_client_secret"
}
```

### 2. Proces autoryzacji
```bash
1. Użytkownik klika "Zaloguj do YouTube"
2. Otwiera się przeglądarka z Google OAuth
3. Użytkownik loguje się i daje uprawnienia
4. Google przekierowuje na localhost:14321/callback?code=...
5. Tauri app przechwytuje code i wymienia na tokeny
6. Tokeny zapisywane lokalnie w ~/.ytlite/tokens.json
```

### 3. Integracja z YTLite
```python
# YTLite automatycznie odczytuje tokeny
from src.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
uploader.upload_video("moje_video.mp4")
```

## 🔧 API Commands (Rust ↔ React)

### Frontend (React) wywołuje backend (Rust):

```typescript
// Sprawdź konfigurację
const config = await invoke('get_config')

// Zapisz OAuth credentials
await invoke('set_config', { 
  clientId: 'xxx', 
  clientSecret: 'yyy' 
})

// Rozpocznij proces OAuth
await invoke('start_oauth')

// Wymień authorization code na tokeny
await invoke('exchange_code', { code: 'auth_code' })

// Odśwież tokeny
const tokens = await invoke('refresh_tokens')

// Sprawdź aktualne tokeny
const tokens = await invoke('check_tokens')

// Test API - lista kanałów
const channels = await invoke('youtube_list_channels')

// Generuj zawartość .env dla YTLite
const env = await invoke('generate_env')
```

## 📂 Pliki konfiguracyjne

### `~/.ytlite/config.json`
```json
{
  "client_id": "xxx.googleusercontent.com",
  "client_secret": "xxx",
  "redirect_uri": "http://127.0.0.1:1420/callback"
}
```

### `~/.ytlite/tokens.json`
```json
{
  "access_token": "ya29.xxx",
  "refresh_token": "1//xxx", 
  "expires_in": 3600,
  "created_at": 1640995200
}
```

## 🔐 Bezpieczeństwo

- **Lokalne przechowywanie**: Tokeny tylko na twoim komputerze
- **HTTPS nie wymagane**: localhost exception w OAuth2
- **Tauri sandbox**: Frontend izolowany od systemu
- **Rust backend**: Memory-safe handling tokenów

## 🐛 Troubleshooting

### Częste problemy:

1. **"Invalid redirect URI"**
   ```bash
   # Sprawdź dokładnie URI w Google Console
   http://127.0.0.1:14321/callback  # nie localhost!
   ```

2. **Tauri dev nie startuje**
   ```bash
   # Sprawdź wersję Rust
   rustc --version  # powinna być 1.70+
   
   # Przebuduj dependencies
   cargo clean && npm run dev
   ```

3. **"Client ID not set"**
   ```bash
   # Najpierw ustaw konfigurację w aplikacji
   # Potem dopiero próbuj OAuth
   ```

## 🔗 Integracja z YTLite

```python
# src/youtube_uploader.py automatycznie używa tokenów
def __init__(self):
    self.tokens_path = Path.home() / '.ytlite' / 'tokens.json'
    self.load_tokens()

def load_tokens(self):
    if self.tokens_path.exists():
        with open(self.tokens_path) as f:
            self.tokens = json.load(f)
```

## 📈 Development

```bash
# Hot reload frontend
npm run vite-dev

# Hot reload z Tauri
npm run dev

# Build dla produkcji
npm run build

# Debug Rust backend
RUST_LOG=debug npm run dev
```

---

**Tauri OAuth App - Bezpieczny bridge między YTLite a YouTube API** 🔐
