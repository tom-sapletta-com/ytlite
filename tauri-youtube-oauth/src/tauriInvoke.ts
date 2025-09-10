// A thin wrapper around Tauri's invoke with a browser fallback for E2E.
// If Tauri runtime is not available (pure web/E2E), we mock responses.

export async function invoke(cmd: string, args?: Record<string, any>): Promise<any> {
  // If Tauri is present, use real invoke
  try {
    // @ts-ignore
    if (typeof window !== 'undefined' && (window as any).__TAURI_IPC__) {
      const mod = await import('@tauri-apps/api/tauri')
      return mod.invoke(cmd, args)
    }
  } catch (e) {
    // fallthrough to mock
  }
  // Fallback mock for E2E/browser
  return mockInvoke(cmd, args)
}

function mockInvoke(cmd: string, _args?: Record<string, any>): Promise<any> {
  switch (cmd) {
    case 'get_config':
      return Promise.resolve(null)
    case 'set_config':
      return Promise.resolve(null)
    case 'start_oauth':
      return Promise.resolve(null)
    case 'exchange_code':
      return Promise.resolve({ access_token: 'mock_access', refresh_token: 'mock_refresh', expires_in: 3600 })
    case 'check_tokens':
      return Promise.resolve({ access_token: '', refresh_token: '' })
    case 'refresh_tokens':
      return Promise.resolve({ access_token: 'mock_access_refreshed', refresh_token: 'mock_refresh' })
    case 'youtube_list_channels':
      return Promise.resolve({ items: [{ id: 'c1', snippet: { title: 'Channel 1' } }] })
    case 'generate_env':
      return Promise.resolve('YOUTUBE_CLIENT_ID=abc\nYOUTUBE_CLIENT_SECRET=xyz')
    default:
      return Promise.resolve(null)
  }
}
