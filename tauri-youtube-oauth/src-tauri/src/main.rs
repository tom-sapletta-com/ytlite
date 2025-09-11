#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{
    Builder, Context, Config, Invoke, PackageInfo, Pattern,
};
use std::sync::Arc;

fn main() {
    let config = Config::default();
    let package_info = PackageInfo {
        name: "tauri-youtube-oauth".to_string(),
        version: "0.1.0".to_string(),
        authors: "".to_string(),
        description: "YouTube OAuth App".to_string(),
    };
    
    Builder::default()
        .invoke_handler(|invoke: Invoke| {
            // Empty handler for minimal setup
            invoke.resolver.respond(Ok(serde_json::Value::Null));
        })
        .run(Context::new(
            config,
            Arc::new(tauri::EmbeddedAssets::default()), // assets
            None, // Option<Icon>
            None, // Option<Vec<u8>>
            None, // Option<Icon>
            package_info,
            (), // system_tray_icon_as_template
            Pattern::Brownfield(std::marker::PhantomData),
            tauri::ShellScopeConfig {
                open: String::new(),
                scopes: std::collections::HashMap::new(),
            }
        ))
        .expect("error while running tauri application");
}
