#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{
    Builder, Invoke,
};

fn main() {
    Builder::default()
        .invoke_handler(|invoke: Invoke| {
            // Empty handler for minimal setup
            invoke.resolver.respond(Ok(serde_json::Value::Null));
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
