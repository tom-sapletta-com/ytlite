#[cfg(test)]
mod tests {
    use tauri_youtube_oauth::{get_config, set_config, check_tokens, write_tokens, Tokens, AppConfig};
    use tauri::test;

    #[tokio::test]
    async fn test_set_and_get_config() {
        let (app, _window) = test::mock_builder()
            .invoke_handler(tauri::generate_handler![get_config, set_config])
            .build(|_context| Ok(())).unwrap();
        let app_handle = app.handle();

        let client_id = "test_client_id".to_string();
        let client_secret = "test_client_secret".to_string();

        set_config(app_handle.clone(), client_id.clone(), client_secret.clone()).await.unwrap();

        let config = get_config(app_handle).await.unwrap().unwrap();

        assert_eq!(config.client_id, client_id);
        assert_eq!(config.client_secret, client_secret);
    }

    #[tokio::test]
    async fn test_check_tokens() {
        let (app, _window) = test::mock_builder()
            .invoke_handler(tauri::generate_handler![check_tokens, write_tokens])
            .build(|_context| Ok(())).unwrap();
        let app_handle = app.handle();

        let tokens = Tokens {
            access_token: "test_access_token".to_string(),
            refresh_token: "test_refresh_token".to_string(),
            expires_in: 3600,
            created_at: 0,
        };
        write_tokens(&app_handle, &tokens).unwrap();

        let checked_tokens = check_tokens(app_handle).await.unwrap();

        assert_eq!(checked_tokens.access_token, "test_access_token");
        assert_eq!(checked_tokens.refresh_token, "test_refresh_token");
    }
}
