import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import App from './App'

// Mock Tauri invoke API
vi.mock('@tauri-apps/api/tauri', () => {
  return {
    invoke: (cmd: string, _args?: any) => {
      switch (cmd) {
        case 'get_config':
          return Promise.resolve(null)
        case 'check_tokens':
          return Promise.resolve({ access_token: '', refresh_token: '' })
        case 'generate_env':
          return Promise.resolve('YOUTUBE_CLIENT_ID=abc\nYOUTUBE_CLIENT_SECRET=xyz')
        case 'youtube_list_channels':
          return Promise.resolve({ items: [{ id: 'c1', snippet: { title: 'Channel 1' } }] })
        case 'start_oauth':
          return Promise.resolve()
        case 'refresh_tokens':
          return Promise.resolve({ access_token: 'acc', refresh_token: 'ref' })
        case 'set_config':
          return Promise.resolve()
        default:
          return Promise.resolve(null)
      }
    },
  }
})

// Stub clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
})

describe('App', () => {
  it('renders UI with main controls', async () => {
    render(<App />)

    expect(await screen.findByText(/Tauri YouTube OAuth/i)).toBeInTheDocument()
    expect(screen.getByText('Zaloguj do YouTube')).toBeInTheDocument()
    expect(screen.getByText('Pobierz kanały')).toBeInTheDocument()
    expect(screen.getByText(/Generuj \.env/)).toBeInTheDocument()
  })

  it('copies generated .env to clipboard', async () => {
    render(<App />)

    fireEvent.click(screen.getByText(/Generuj \.env \(kopiuj do schowka\)/))

    await waitFor(() => {
      expect(screen.getByText(/Skopiowano zawartość \.env do schowka/i)).toBeInTheDocument()
    })
  })

  it('fetches channels and renders list', async () => {
    render(<App />)

    fireEvent.click(screen.getByText('Pobierz kanały'))

    await waitFor(() => {
      expect(screen.getByText('Channel 1')).toBeInTheDocument()
    })
  })
})
