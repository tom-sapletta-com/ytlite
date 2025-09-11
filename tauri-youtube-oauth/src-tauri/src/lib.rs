#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::{fs, path::{Path, PathBuf}, process::Command, time::{SystemTime, UNIX_EPOCH}};
use tauri::AppHandle;
use warp::Filter;

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct Tokens {
  pub access_token: String,
  pub refresh_token: String,
  #[serde(default)]
  pub expires_in: u64,
  #[serde(default)]
  pub created_at: u64,
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct AppConfig {
  pub client_id: String,
  pub client_secret: String,
}

fn now_secs() -> u64 {
  SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs()
}

fn app_config_dir(app: &AppHandle) -> Result<PathBuf, String> {
  app
    .path_resolver()
    .app_config_dir()
    .ok_or_else(|| "no app config dir".to_string())
}

fn config_path(app: &AppHandle) -> Result<PathBuf, String> { Ok(app_config_dir(app)?.join("oauth_config.json")) }
fn tokens_path(app: &AppHandle) -> Result<PathBuf, String> { Ok(app_config_dir(app)?.join("tokens.json")) }

fn read_config_from_dir(dir: &Path) -> Option<AppConfig> {
  let p = dir.join("oauth_config.json");
  let s = fs::read_to_string(p).ok()?;
  serde_json::from_str(&s).ok()
}

fn write_config_to_dir(dir: &Path, cfg: &AppConfig) -> Result<(), String> {
  fs::create_dir_all(dir).map_err(|e| e.to_string())?;
  let p = dir.join("oauth_config.json");
  let s = serde_json::to_string_pretty(cfg).map_err(|e| e.to_string())?;
  fs::write(p, s).map_err(|e| e.to_string())
}

fn read_tokens_from_dir(dir: &Path) -> Option<Tokens> {
  let p = dir.join("tokens.json");
  let s = fs::read_to_string(p).ok()?;
  serde_json::from_str(&s).ok()
}

fn write_tokens_to_dir(dir: &Path, t: &Tokens) -> Result<(), String> {
  fs::create_dir_all(dir).map_err(|e| e.to_string())?;
  let p = dir.join("tokens.json");
  let s = serde_json::to_string_pretty(t).map_err(|e| e.to_string())?;
  fs::write(p, s).map_err(|e| e.to_string())
}

fn read_config(app: &AppHandle) -> Option<AppConfig> { read_config_from_dir(&app_config_dir(app).ok()?) }
fn write_config(app: &AppHandle, cfg: &AppConfig) -> Result<(), String> { write_config_to_dir(&app_config_dir(app)?, cfg) }
fn read_tokens(app: &AppHandle) -> Option<Tokens> { read_tokens_from_dir(&app_config_dir(app).ok()?) }
pub fn write_tokens(app: &AppHandle, t: &Tokens) -> Result<(), String> { write_tokens_to_dir(&app_config_dir(app)?, t) }

fn token_endpoint() -> String {
  std::env::var("OAUTH_TOKEN_URL").unwrap_or_else(|_| "https://oauth2.googleapis.com/token".to_string())
}

async fn perform_token_exchange(client_id: &str, client_secret: &str, code: &str, redirect: &str) -> Result<Tokens, String> {
  let params = [
    ("code", code),
    ("client_id", client_id),
    ("client_secret", client_secret),
    ("redirect_uri", redirect),
    ("grant_type", "authorization_code"),
  ];
  let client = reqwest::Client::new();
  let resp = client.post(&token_endpoint()).form(&params).send().await.map_err(|e| e.to_string())?;
  let json: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
  let access = json.get("access_token").and_then(|v| v.as_str()).unwrap_or_default().to_string();
  let refresh = json.get("refresh_token").and_then(|v| v.as_str()).unwrap_or_default().to_string();
  let expires_in = json.get("expires_in").and_then(|v| v.as_u64()).unwrap_or(0);
  if access.is_empty() { return Err(format!("Błąd wymiany tokenów: {}", json)); }
  Ok(Tokens { access_token: access, refresh_token: refresh, expires_in, created_at: now_secs() })
}

async fn exchange_and_persist(cfg_dir: &Path, code: &str) -> Result<Tokens, String> {
  let cfg: AppConfig = read_config_from_dir(cfg_dir).ok_or("Brak konfiguracji klienta".to_string())?;
  let redirect = "http://127.0.0.1:14321/callback";
  let t = perform_token_exchange(&cfg.client_id, &cfg.client_secret, code, redirect).await?;
  write_tokens_to_dir(cfg_dir, &t)?;
  Ok(t)
}

async fn start_oauth(app: AppHandle) -> Result<(), String> {
  let cfg = read_config(&app).ok_or("Brak konfiguracji klienta (Client ID/Secret)".to_string())?;
  let redirect = "http://127.0.0.1:14321/callback";
  let scope = "https://www.googleapis.com/auth/youtube.readonly";
  let url = format!(
    "https://accounts.google.com/o/oauth2/v2/auth?client_id={}&response_type=code&redirect_uri={}&access_type=offline&prompt=consent&scope={}",
    urlencoding::encode(&cfg.client_id),
    urlencoding::encode(redirect),
    urlencoding::encode(scope)
  );

  // Open default browser
  #[cfg(target_os = "windows")]
  { let _ = Command::new("cmd").args(["/C", "start", &url]).spawn(); }
  #[cfg(target_os = "macos")]
  { let _ = Command::new("open").arg(&url).spawn(); }
  #[cfg(all(unix, not(target_os = "macos")))]
  { let _ = Command::new("xdg-open").arg(&url).spawn(); }

  Ok(())
}

pub async fn exchange_code(app: AppHandle, code: String) -> Result<Tokens, String> {
  let dir = app_config_dir(&app)?;
  exchange_and_persist(&dir, &code).await
}

async fn refresh_tokens(app: AppHandle) -> Result<Tokens, String> {
  let cfg = read_config(&app).ok_or("Brak konfiguracji klienta".to_string())?;
  let mut t = read_tokens(&app).ok_or("Brak zapisanych tokenów".to_string())?;
  if t.refresh_token.is_empty() {
    return Err("Brak refresh_token — zaloguj się ponownie".into());
  }
  let params = [
    ("client_id", cfg.client_id.as_str()),
    ("client_secret", cfg.client_secret.as_str()),
    ("refresh_token", t.refresh_token.as_str()),
    ("grant_type", "refresh_token"),
  ];
  let client = reqwest::Client::new();
  let resp = client
    .post(&token_endpoint())
    .form(&params)
    .send()
    .await
    .map_err(|e| e.to_string())?;
  let json: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
  let access = json.get("access_token").and_then(|v| v.as_str()).unwrap_or("").to_string();
  let expires_in = json.get("expires_in").and_then(|v| v.as_u64()).unwrap_or(0);
  if access.is_empty() { return Err(format!("Błąd odświeżania: {}", json)); }
  t.access_token = access;
  t.expires_in = expires_in;
  t.created_at = now_secs();
  write_tokens(&app, &t)?;
  Ok(t)
}

pub async fn youtube_list_channels(app: AppHandle) -> Result<serde_json::Value, String> {
  let mut t = read_tokens(&app).ok_or("Brak tokenów — zaloguj się".to_string())?;
  // Auto refresh if expired (buffer 60s)
  if t.expires_in > 0 && now_secs().saturating_sub(t.created_at) + 60 > t.expires_in {
    let _ = refresh_tokens(app.clone()).await; // try refresh, ignore error here
    t = read_tokens(&app).ok_or("Brak tokenów po odświeżeniu".to_string())?;
  }
  let client = reqwest::Client::new();
  let url = "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true";
  let resp = client
    .get(url)
    .bearer_auth(&t.access_token)
    .send()
    .await
    .map_err(|e| e.to_string())?;
  if !resp.status().is_success() {
    let text = resp.text().await.unwrap_or_default();
    return Err(format!("YouTube API error: {}", text));
  }
  Ok(resp.json().await.map_err(|e| e.to_string())?)
}

pub async fn generate_env(app: AppHandle) -> Result<String, String> {
  let cfg = read_config(&app).unwrap_or_default();
  let t = read_tokens(&app).unwrap_or_default();
  Ok(format_env_text(&cfg, &t))
}

fn format_env_text(cfg: &AppConfig, t: &Tokens) -> String {
  format!(
    "# Generated by Tauri YouTube OAuth\nYOUTUBE_CLIENT_ID={}\nYOUTUBE_CLIENT_SECRET={}\nUPLOAD_PRIVACY=unlisted\nAUTO_UPLOAD=false\n\n# Optional (not recommended to store in .env)\n# YOUTUBE_ACCESS_TOKEN={}\n# YOUTUBE_REFRESH_TOKEN={}\n",
    cfg.client_id,
    cfg.client_secret,
    t.access_token,
    t.refresh_token
  )
}

// Removed duplicate import to fix build error
// use tauri::AppHandle;

pub fn setup() {
    // Placeholder for future functionality
}
