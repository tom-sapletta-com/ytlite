#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::{fs, path::PathBuf, process::Command, time::{SystemTime, UNIX_EPOCH}};
use tauri::{AppHandle, Manager};

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
struct Tokens {
  access_token: String,
  refresh_token: String,
  #[serde(default)]
  expires_in: u64,
  #[serde(default)]
  created_at: u64,
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
struct AppConfig {
  client_id: String,
  client_secret: String,
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

fn config_path(app: &AppHandle) -> Result<PathBuf, String> {
  Ok(app_config_dir(app)?.join("oauth_config.json"))
}

fn tokens_path(app: &AppHandle) -> Result<PathBuf, String> {
  Ok(app_config_dir(app)?.join("tokens.json"))
}

fn read_config(app: &AppHandle) -> Option<AppConfig> {
  let path = config_path(app).ok()?;
  let s = fs::read_to_string(path).ok()?;
  serde_json::from_str(&s).ok()
}

fn write_config(app: &AppHandle, cfg: &AppConfig) -> Result<(), String> {
  let dir = app_config_dir(app)?;
  fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
  let p = config_path(app)?;
  let s = serde_json::to_string_pretty(cfg).map_err(|e| e.to_string())?;
  fs::write(p, s).map_err(|e| e.to_string())
}

fn read_tokens(app: &AppHandle) -> Option<Tokens> {
  let p = tokens_path(app).ok()?;
  let s = fs::read_to_string(p).ok()?;
  serde_json::from_str(&s).ok()
}

fn write_tokens(app: &AppHandle, t: &Tokens) -> Result<(), String> {
  let dir = app_config_dir(app)?;
  fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
  let p = tokens_path(app)?;
  let s = serde_json::to_string_pretty(t).map_err(|e| e.to_string())?;
  fs::write(p, s).map_err(|e| e.to_string())
}

#[tauri::command]
async fn get_config(app: AppHandle) -> Result<Option<AppConfig>, String> {
  Ok(read_config(&app))
}

#[tauri::command]
async fn set_config(app: AppHandle, client_id: String, client_secret: String) -> Result<(), String> {
  let cfg = AppConfig { client_id, client_secret };
  write_config(&app, &cfg)
}

#[tauri::command]
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

#[tauri::command]
async fn exchange_code(app: AppHandle, code: String) -> Result<Tokens, String> {
  let cfg = read_config(&app).ok_or("Brak konfiguracji klienta".to_string())?;
  let redirect = "http://127.0.0.1:14321/callback";
  let params = [
    ("code", code.as_str()),
    ("client_id", cfg.client_id.as_str()),
    ("client_secret", cfg.client_secret.as_str()),
    ("redirect_uri", redirect),
    ("grant_type", "authorization_code"),
  ];

  let client = reqwest::Client::new();
  let resp = client
    .post("https://oauth2.googleapis.com/token")
    .form(&params)
    .send()
    .await
    .map_err(|e| e.to_string())?;

  let json: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
  let access = json.get("access_token").and_then(|v| v.as_str()).unwrap_or_default().to_string();
  let refresh = json.get("refresh_token").and_then(|v| v.as_str()).unwrap_or_default().to_string();
  let expires_in = json.get("expires_in").and_then(|v| v.as_u64()).unwrap_or(0);

  if access.is_empty() {
    return Err(format!("Błąd wymiany tokenów: {}", json));
  }

  let t = Tokens { access_token: access, refresh_token: refresh, expires_in, created_at: now_secs() };
  write_tokens(&app, &t)?;
  Ok(t)
}

#[tauri::command]
async fn check_tokens(app: AppHandle) -> Result<Tokens, String> {
  Ok(read_tokens(&app).unwrap_or_default())
}

#[tauri::command]
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
    .post("https://oauth2.googleapis.com/token")
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

#[tauri::command]
async fn youtube_list_channels(app: AppHandle) -> Result<serde_json::Value, String> {
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

#[tauri::command]
async fn generate_env(app: AppHandle) -> Result<String, String> {
  let cfg = read_config(&app).unwrap_or_default();
  let t = read_tokens(&app).unwrap_or_default();
  let env_text = format!(
    "# Generated by Tauri YouTube OAuth\nYOUTUBE_CLIENT_ID={}\nYOUTUBE_CLIENT_SECRET={}\nUPLOAD_PRIVACY=unlisted\nAUTO_UPLOAD=false\n\n# Optional (not recommended to store in .env)\n# YOUTUBE_ACCESS_TOKEN={}\n# YOUTUBE_REFRESH_TOKEN={}\n",
    cfg.client_id,
    cfg.client_secret,
    t.access_token,
    t.refresh_token
  );
  Ok(env_text)
}

fn main() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
      get_config,
      set_config,
      start_oauth,
      exchange_code,
      check_tokens,
      refresh_tokens,
      youtube_list_channels,
      generate_env
    ])
    .setup(|app| {
      // Ensure config dir exists
      if let Ok(dir) = app_config_dir(&app.handle()) { let _ = fs::create_dir_all(dir.clone());
        // Spawn the OAuth callback server using the app's config dir
        let tokens_file = dir.join("tokens.json");
        let config_file = dir.join("oauth_config.json");
        std::thread::spawn(move || {
          let rt = tokio::runtime::Builder::new_multi_thread().enable_all().build().expect("tokio runtime");
          rt.block_on(async move {
            let route = warp::path("callback")
              .and(warp::get())
              .and(warp::query::<std::collections::HashMap<String, String>>())
              .map(move |params: std::collections::HashMap<String, String>| {
                let code = params.get("code").cloned();
                let tokens_file = tokens_file.clone();
                let config_file = config_file.clone();
                tokio::spawn(async move {
                  if let Some(code) = code {
                    let cfg_text = std::fs::read_to_string(&config_file).unwrap_or_default();
                    let cfg: Option<AppConfig> = serde_json::from_str(&cfg_text).ok();
                    if let Some(cfg) = cfg {
                      let redirect = "http://127.0.0.1:14321/callback";
                      let params = [
                        ("code", code.as_str()),
                        ("client_id", cfg.client_id.as_str()),
                        ("client_secret", cfg.client_secret.as_str()),
                        ("redirect_uri", redirect),
                        ("grant_type", "authorization_code"),
                      ];
                      let client = reqwest::Client::new();
                      if let Ok(resp) = client.post("https://oauth2.googleapis.com/token").form(&params).send().await {
                        if let Ok(json) = resp.json::<serde_json::Value>().await {
                          let access = json.get("access_token").and_then(|v| v.as_str()).unwrap_or("").to_string();
                          let refresh = json.get("refresh_token").and_then(|v| v.as_str()).unwrap_or("").to_string();
                          let expires_in = json.get("expires_in").and_then(|v| v.as_u64()).unwrap_or(0);
                          if !access.is_empty() {
                            let t = Tokens { access_token: access, refresh_token: refresh, expires_in, created_at: now_secs() };
                            if let Ok(s) = serde_json::to_string_pretty(&t) {
                              let _ = std::fs::write(&tokens_file, s);
                            }
                          }
                        }
                      }
                    }
                  }
                });
                warp::reply::html("<html><body><h2>Autoryzacja zakończona. Możesz zamknąć to okno.</h2></body></html>")
              });
            warp::serve(route).run(([127, 0, 0, 1], 14321)).await;
          });
        });
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
