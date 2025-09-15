Dodaj mozliwosc uzywania GUI w przegaldarce do wygenerowania w czasie rzeczywistym zopopgodladem jednego projektu
na podstawie pliku markdown z danymi .env 
pozowl na tworzenie roznych proejtkow na ropzne konta youtube, gdzie
dane wrazliwe sa przechopwywane w .env dla danego projektu w danym folderze


generuj samodzielnie, nie pytaj o uruchmienie skrytpow i komend, pisz wlasne skrypyt uruchamiajc rozne uslugi, zamiast pytac usera, dodaj bardziej zlozone odpytywanie o bledy, stworz liste check z e skrytpami, aby zbadac co moze byc problemem automatycznie poorpzez generowanie logo zaawansowanych w formacie json w pliku dla llm



dodaj publikacje na wordpress z pobeiraniem danych logowania i do api z .env w taki sposob, aby mozliwe bylo uplodaowanie tresci do wielu zrodel, blogow, social mediow
pobieraj z poprzez integracje ze storages jak nextclo
ał make validate-app i make validate-data i streścił wynik i tworzyl raporty dla kazdego uruchomienia aplikacji w folderze pprojektu
- dodaj więcej głosów do wyboru z możliwością wyboru w web gui
- więcej typów prezentacji konwertowanych do video nie tylko sam text ale też templates z różnymi kolorami i wielkościami font
- możliwośc korzystania z API do poopularnych serwisów, które będą generowały video z tekstu i powierzonych grafik i video
- dodaj do generowanych tresci obsluge fontow z roznych jezykow, dopasuj font do jezyka aby obslugiwal np polskie, niemieckie napisy, wspieraj utf8 w dokumentacji

- zamiast wielu plikow w folderze projektu, np. output/projects/dochodzenie używaj jednego pliku SVG z danymi tetkstowymi jako metadanymi, a dane typu mp4 lub mp3/wav trzymaj w datauri i edytuj wybrane fragmenty pliku SVG podczas np reedeycji, pozwalaj zmieniać metadane pw edytorze wybierajac z listy projektow wybrany plik SVG , nadpisuj po wygenerowaniu też w datauri generowane media, 
- zadbaj o miniaturke dla SVG, aby był jednoczesnie grafika miniaturki video

- do celow testowych stworz w docker wordpress, na ktorym bedzie publikowany artykul i video, stworz przykladowy projekt z danymi logowania, aby zrobić publikacje tego wygenerowane projektu 

- po otwarciu svg w przegaldarce powinno byc mozliwe zobaczenie wszystkich metadanych oraz na samej gorze video powinno sie urchomic w trybie odtwarzania
- po otwarciu strony http://127.0.0.1:5000/ powinno byc mozliwe wybranie z listy projektu SVG , poporzez sprawdzenie folderow w projects

przeprowadz refaktoryzacje plikow, ktore maja wiecej niz 500 linii podziel je na mniejsze komponenty, zadbaj o modularnosc i komplementarnosc projektu
- dodaj do listy projektow: widok listy szczegolowej jak w tabeli z przelaczaniem: tabela/grid
- pliki SVG i wchodzace w sklad niego media powinny byc podczas edycji i tworzenia byc walidowane pod wzgledem poporawnosci


- podczas preview w systemie powinno byc widoczne preview miniaturki video 
- po otwarciu SVG w przegaldarce powinno byc automatycznie odtwarzanie video, ktore znajduje sie w datauri
- stworz komende make test-data sparwdzaj zawartosc fodlerow projektow i testuj pliki mediow i SVG w poszukiwwaniu bledow, usuwaj wszystkie wadliwe pliki
- 
- podczas generowania plikow SVG, gdy wystapi blad podczas generowania pliku mediow lub SVG wyswietlaj logi w konsoli i w plikach logow
- rozszerz informacje o logach, waliduj glebiej podczas uruchamiani amake validate, gdyz aktualnie jest za malo danych szczegolowych lub nei sa podawane:
Transcribing /tmp/extracted_audio_test_lang_es.wav...
Validating output/videos/test_lang_it.mp4
Transcribing /tmp/extracted_audio_test_lang_it.wav...
Validating output/videos/wordpress-test.mp4
Transcribing /tmp/extracted_audio_wordpress-test.wav...
Validating output/videos/integration_test_project.mp4
Transcribing /tmp/extracted_audio_integration_test_project.wav...
✓ Report saved to output/validation_report.json
                         Video Validation Report                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Video                    ┃ Status  ┃ Duration ┃ Quality ┃ Audio Match ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━┩
│ e2e_valid                │ ✗ Error │ N/A      │ F       │ N/A         │
│ e2e_badfm                │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_voice_pl_marek      │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_voice_pl_zofia      │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_voice_de_killian    │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_voice_de_katja      │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_voice_en_guy        │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_voice_en_aria       │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_json_project        │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_tech_classic        │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_tech_gradient       │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_tech_boxed          │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_tech_left           │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_philosophy_classic  │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_philosophy_gradient │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_philosophy_boxed    │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_philosophy_left     │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_wetware_classic     │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_wetware_gradient    │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_wetware_boxed       │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_wetware_left        │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_font_24             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_font_36             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_font_48             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_font_64             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_font_72             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_font_96             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_lang_pl             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_lang_en             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_lang_de             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_lang_fr             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_lang_es             │ ✗ Error │ N/A      │ F       │ N/A         │
│ test_lang_it             │ ✗ Error │ N/A      │ F       │ N/A         │
│ wordpress-test           │ ✗ Error │ N/A      │ F       │ N/A         │
│ integration_test_project │ ✗ Error │ N/A      │ F       │ N/A         │
└──────────────────────────┴─────────┴──────────┴─────────┴─────────────┘

przed wykonaniem filmu zrob tez pierwsza strone wedle template html z domyslnymi wartosciami podanymi w .env i metadanych, chiodzi o autora, nazwe filmu, licencja itd
oraz nadpisanymi wartosciami podanymi w edycji projektu
wszystkie metadane powinny być edytowalne w trakcie itworzeni i edycji jako pola tekstwoe lub selectlist w zaleznosci do typu lub checkbox jesli boolean
po wygenerowaniu filmu tworz miniaturki dla 33% i 66% czasu trwania filmu w celu podgladu co znajduje sie w filmie


po wykonaniu filmu stworz miniaturke

- do tabeli z widokiem listy projektow dodaj sortowanie po nazwie i czasie utworzenia i czasie aaktualizacji/edycji
- dodaj tez do kazdego projektu mala miniaturke 64px


