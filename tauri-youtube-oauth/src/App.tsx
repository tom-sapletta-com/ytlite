import React, { useEffect, useMemo, useState } from 'react'
import { invoke } from './tauriInvoke'
import ProgressBar from './components/ProgressBar'

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

interface Voice {
  language: string
  gender: string
  description: string
}

interface Template {
  name: string
  description: string
  background_color: string
  text_color: string
  font_size: number
  font_family: string
}

export default function App() {
  const [status, setStatus] = useState('')
  const [tokens, setTokens] = useState<Tokens | null>(null)
  const [channels, setChannels] = useState<any[]>([])
  const [cfg, setCfg] = useState<AppConfig>({ client_id: '', client_secret: '' })
  const [isCallback, setIsCallback] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [totalSteps, setTotalSteps] = useState(6)
  const [currentDescription, setCurrentDescription] = useState('')
  const [voices, setVoices] = useState<Record<string, Voice>>({})
  const [selectedVoice, setSelectedVoice] = useState('pl-PL-MarekNeural')
  const [templates, setTemplates] = useState<Record<string, Template>>({})
  const [selectedTemplate, setSelectedTemplate] = useState('default')

  useEffect(() => {
    setIsCallback(typeof window !== 'undefined' && window.location.pathname === '/callback')
  }, [])

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

      try {
        const v = (await invoke('get_voices')) as Record<string, Voice>
        setVoices(v)
      } catch {}

      try {
        const t = (await invoke('get_templates')) as Record<string, Template>
        setTemplates(t)
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

  const handleProcessContent = async () => {
    setIsProcessing(true)
    setCurrentStep(1)
    setCurrentDescription('Parsing content...')

    // Simulate processing steps (replace with actual processing logic)
    setTimeout(() => {
      setCurrentStep(2)
      setCurrentDescription('Preparing output paths...')
    }, 1000)
    setTimeout(() => {
      setCurrentStep(3)
      setCurrentDescription(`Generating audio with voice: ${selectedVoice}...`)
    }, 2000)
    setTimeout(() => {
      setCurrentStep(4)
      setCurrentDescription('Creating slides...')
    }, 3000)
    setTimeout(() => {
      setCurrentStep(5)
      setCurrentDescription('Creating video...')
    }, 4000)
    setTimeout(() => {
      setCurrentStep(6)
      setCurrentDescription('Generating shorts...')
    }, 5000)
    setTimeout(() => {
      setIsProcessing(false)
      setCurrentStep(0)
      setCurrentDescription('')
    }, 6000)

    // Actual invocation of backend processing with selected voice and template
    try {
      await invoke('process_content', { voice: selectedVoice, template: selectedTemplate })
    } catch (error) {
      console.error('Error processing content:', error)
    }
  }

  const handleVoiceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedVoice(event.target.value)
  }

  const handleTemplateChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedTemplate(event.target.value)
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

      <section style={{ margin: '20px 0' }}>
        <h2>Wybór głosu i szablonu</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 640 }}>
          <label>
            Wybierz głos:
            <select value={selectedVoice} onChange={handleVoiceChange}>
              {Object.entries(voices).map(([id, details]) => (
                <option key={id} value={id}>{details.description}</option>
              ))}
            </select>
          </label>
          <label>
            Wybierz szablon:
            <select value={selectedTemplate} onChange={handleTemplateChange}>
              {Object.entries(templates).map(([id, details]) => (
                <option key={id} value={id}>{details.name} - {details.description}</option>
              ))}
            </select>
          </label>
          <div>
            <button onClick={handleProcessContent} disabled={isProcessing}>
              {isProcessing ? 'Przetwarzanie...' : 'Przetwórz zawartość'}
            </button>
          </div>
        </div>
      </section>

      {isProcessing && (
        <ProgressBar currentStep={currentStep} totalSteps={totalSteps} currentDescription={currentDescription} />
      )}

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
