import { invoke } from '@tauri-apps/api/tauri'

export interface Tokens {
  access_token: string
  refresh_token: string
  expires_in?: number
  created_at?: number
}

export interface AppConfig {
  client_id: string
  client_secret: string
}

export async function getConfig(): Promise<AppConfig | null> {
  return (await invoke('get_config')) as any
}

export async function setConfig(client_id: string, client_secret: string) {
  await invoke('set_config', { clientId: client_id, clientSecret: client_secret })
}

export async function startOAuth() {
  await invoke('start_oauth')
}

export async function checkTokens(): Promise<Tokens | null> {
  return (await invoke('check_tokens')) as any
}

export async function refreshTokens(): Promise<Tokens | null> {
  return (await invoke('refresh_tokens')) as any
}

export async function youtubeListChannels(): Promise<any> {
  return await invoke('youtube_list_channels')
}

export async function generateEnv(): Promise<string> {
  return (await invoke('generate_env')) as string
}
