# Page snapshot

```yaml
- generic [ref=e3]:
  - heading "Tauri YouTube OAuth" [level=1] [ref=e4]
  - paragraph [ref=e5]: "Status: Błąd: NotAllowedError: Failed to execute 'writeText' on 'Clipboard': Write permission denied."
  - generic [ref=e6]:
    - heading "Konfiguracja OAuth (Client ID/Secret)" [level=2] [ref=e7]
    - generic [ref=e8]:
      - generic [ref=e9]:
        - text: Client ID
        - textbox "Client ID" [ref=e10]
      - generic [ref=e11]:
        - text: Client Secret
        - textbox "Client Secret" [ref=e12]
      - button "Zapisz konfigurację" [ref=e14]
  - generic [ref=e15]:
    - heading "Autoryzacja" [level=2] [ref=e16]
    - button "Zaloguj do YouTube" [ref=e17]
    - button "Sprawdź tokeny" [ref=e18]
    - button "Odśwież token" [ref=e19]
    - button "Generuj .env (kopiuj do schowka)" [active] [ref=e20]
  - generic [ref=e21]:
    - 'heading "API: Lista kanałów" [level=2] [ref=e22]'
    - button "Pobierz kanały" [ref=e23]
    - list
  - generic [ref=e24]:
    - heading "Instrukcje" [level=3] [ref=e25]
    - list [ref=e26]:
      - listitem [ref=e27]: Uzupełnij Client ID i Secret, a następnie zapisz.
      - listitem [ref=e28]: "W konsoli Google dodaj Redirect URI: http://127.0.0.1:1420/callback."
      - listitem [ref=e29]: Kliknij "Zaloguj do YouTube" i przejdź proces OAuth.
      - listitem [ref=e30]: Po autoryzacji wrócisz do /callback, a tokeny zostaną zapisane.
```