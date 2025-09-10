import React, { useEffect, useMemo, useState } from 'react'
import { invoke } from './tauriInvoke'

interface Tokens {
  access_token: string
  refresh_token: string
  expires_in?: number
  created_at?: number
}

interface AppConfig {
  client_id: string
  client_secret: string
}

export default function App() {
  const [status, setStatus] = useState('')
  const [tokens, setTokens] = useState<Tokens | null>(null)
  const [channels, setChannels] = useState<any[]>([])
  const [cfg, setCfg] = useState<AppConfig>({ client_id: '', client_secret: '' })
  const isCallback = typeof window !== 'undefined' && window.location.pathname === '/callback'

  // On mount, if callback path, parse code and exchange
  useEffect(() => {
    if (!isCallback) return
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    if (code) {
      setStatus('Wymieniam code na tokeny...')
      invoke('exchange_code', { code })
        .then(() => {
          setStatus('Autoryzacja zakończona. Możesz zamknąć to okno.')
        })
        .catch((e) => setStatus('Błąd wymiany tokenów: ' + String(e)))
    } else {
      setStatus('Brak parametru code w callbacku')
    }
  }, [isCallback])

  // Load config and tokens initially
  useEffect(() => {
    ;(async () => {
      try {
        const c = (await invoke('get_config')) as AppConfig | null
        if (c) setCfg(c)
      } catch {}

      try {
        const t = (await invoke('check_tokens')) as Tokens
        if (t && t.access_token) setTokens(t)
      } catch {}
    })()
  }, [])

  async function saveConfig() {
    setStatus('Zapisuję konfigurację...')
    try {
      await invoke('set_config', { clientId: cfg.client_id, clientSecret: cfg.client_secret })
      setStatus('Konfiguracja zapisana')
    } catch (e) {
      setStatus('Błąd zapisu: ' + String(e))
    }
  }

  async function startAuth() {
    setStatus('Otwieranie okna autoryzacji...')
    try {
      await invoke('start_oauth')
      setStatus('Oczekiwanie na autoryzację w przeglądarce...')
    } catch (e) {
      setStatus('Błąd: ' + String(e))
    }
  }

  async function fetchChannels() {
    setStatus('Pobieram kanały z YouTube...')
    try {
      const res: any = await invoke('youtube_list_channels')
      setChannels(res.items || [])
      setStatus('Gotowe')
    } catch (e) {
      setStatus('Błąd: ' + String(e))
    }
  }

  async function refreshTokens() {
    setStatus('Odświeżam token...')
    try {
      const t = (await invoke('refresh_tokens')) as Tokens
      setTokens(t)
      setStatus('Token odświeżony')
    } catch (e) {
      setStatus('Błąd odświeżania: ' + String(e))
    }
  }

  async function loadTokens() {
    try {
      const t = (await invoke('check_tokens')) as Tokens
      setTokens(t)
      setStatus('Tokeny załadowane')
    } catch (e) {
      setStatus('Błąd: ' + String(e))
    }
  }

  async function generateEnv() {
    setStatus('Generuję zawartość .env...')
    try {
      const envText = (await invoke('generate_env')) as string
      await navigator.clipboard.writeText(envText)
      setStatus('Skopiowano zawartość .env do schowka')
    } catch (e) {
      setStatus('Błąd: ' + String(e))
    }
  }

  if (isCallback) {
    return (
      <div style={{ padding: 24, fontFamily: 'system-ui, sans-serif' }}>
        <h1>Callback OAuth</h1>
        <p>{status}</p>
      </div>
    )
  }

  return (
    <div style={{ padding: 24, fontFamily: 'system-ui, sans-serif', lineHeight: 1.6 }}>
      <h1>Tauri YouTube OAuth</h1>
      <p>Status: {status || (tokens?.access_token ? 'Zalogowany' : 'Nie zalogowany')}</p>

      <section style={{ margin: '20px 0' }}>
        <h2>Konfiguracja OAuth (Client ID/Secret)</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 640 }}>
          <label>
            Client ID
            <input
              style={{ width: '100%' }}
              value={cfg.client_id}
              onChange={(e) => setCfg({ ...cfg, client_id: e.target.value })}
              placeholder="YOUTUBE_CLIENT_ID"
            />
          </label>
          <label>
            Client Secret
            <input
              style={{ width: '100%' }}
              value={cfg.client_secret}
              onChange={(e) => setCfg({ ...cfg, client_secret: e.target.value })}
              placeholder="YOUTUBE_CLIENT_SECRET"
            />
          </label>
          <div>
            <button onClick={saveConfig}>Zapisz konfigurację</button>
          </div>
        </div>
      </section>

      <section style={{ margin: '20px 0' }}>
        <h2>Autoryzacja</h2>
        <button onClick={startAuth}>Zaloguj do YouTube</button>
        <button onClick={loadTokens} style={{ marginLeft: 8 }}>
          Sprawdź tokeny
        </button>
        <button onClick={refreshTokens} style={{ marginLeft: 8 }}>
          Odśwież token
        </button>
        <button onClick={generateEnv} style={{ marginLeft: 8 }}>
          Generuj .env (kopiuj do schowka)
        </button>
      </section>

      <section style={{ margin: '20px 0' }}>
        <h2>API: Lista kanałów</h2>
        <button onClick={fetchChannels}>Pobierz kanały</button>
        <ul>
          {channels.map((c: any) => (
            <li key={c.id}>{c?.snippet?.title || c.id}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Instrukcje</h3>
        <ol>
          <li>Uzupełnij Client ID i Secret, a następnie zapisz.</li>
          <li>W konsoli Google dodaj Redirect URI: http://127.0.0.1:1420/callback.</li>
          <li>Kliknij "Zaloguj do YouTube" i przejdź proces OAuth.</li>
          <li>Po autoryzacji wrócisz do /callback, a tokeny zostaną zapisane.</li>
        </ol>
      </section>
    </div>
  )
}
