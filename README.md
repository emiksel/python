 MemoBot, pełni kilka funkcji umożliwiających użytkownikom interakcję z nim na kanale IRC. Jego główne zadania to zapisywanie wiadomości dla użytkowników, ustawianie alarmów i minutników, a także obsługa podstawowych komend. Poniżej przedstawiam szczegółowy opis jego funkcji:

1. Zarządzanie Wiadomościami (MessageManager)
Zapisywanie Wiadomości: Bot może zapisywać wiadomości dla użytkowników, którzy są nieobecni na kanale. Jeśli użytkownik pojawi się ponownie, bot automatycznie wysyła do niego zapisane wiadomości.
Obsługa Komendy !rec: Pozwala użytkownikowi zapisać wiadomość dla innego użytkownika poprzez komendę !rec <nick> <wiadomość>. Jeśli docelowy użytkownik jest obecny na kanale, wiadomość zostanie zapisana i wysłana, gdy ten użytkownik się zaloguje.
2. Zarządzanie Użytkownikami (UserManager)
Dodawanie Użytkowników: Bot śledzi użytkowników obecnych na kanale i aktualizuje listę użytkowników, gdy ktoś dołączy lub opuści kanał.
Usuwanie Użytkowników: Użytkownicy, którzy opuszczają kanał, są usuwani z listy.
Sprawdzanie Obecności: Bot może sprawdzić, czy dany użytkownik jest obecny na kanale.
3. Zarządzanie Alarmami (AlarmManager)
Ustawianie Alarmów: Użytkownicy mogą ustawić alarm na określoną godzinę za pomocą komendy !alarm <HH:MM> <wiadomość>. Bot zapisuje alarm i wysyła przypomnienie na kanał o ustalonej godzinie.
Sprawdzanie Alarmów: Bot w oddzielnym wątku sprawdza ustawione alarmy i wysyła przypomnienia, gdy nadchodzi ich czas.
4. Zarządzanie Minutnikami (TimerManager)
Ustawianie Minutników: Użytkownicy mogą ustawiać minutniki używając komendy !minutnik <czas> <wiadomość>, gdzie czas może być wyrażony w minutach (Xmin) lub godzinach (Xh). Bot informuje na kanale, gdy upłynie ustawiony czas.
Sprawdzanie Minutników: Minutniki są obsługiwane w oddzielnym wątku, który regularnie sprawdza, czy któryś z minutników powinien zostać zakończony i przypomina użytkownikowi o tym fakcie.
5. Obsługa Komend
Komenda !help: Wyświetla listę dostępnych komend i instrukcji, jak z nich korzystać, bezpośrednio na kanale.
6. Utrzymanie Połączenia
Wysyłanie Pingów: Bot wysyła regularne pingy do serwera, aby utrzymać połączenie aktywne.
Automatyczne Ponowne Połączenie: W przypadku rozłączenia bot próbuje ponownie nawiązać połączenie z serwerem IRC.
7. Obsługa Zdarzeń IRC
Dołączanie do Kanału: Bot dołącza do określonego kanału po połączeniu z serwerem.
Odbieranie i Obsługa Wiadomości Publicznych: Bot analizuje wiadomości wysyłane na kanał w celu identyfikacji i przetwarzania komend.
Zarządzanie Listą Użytkowników: Aktualizacja listy użytkowników obecnych na kanale poprzez zdarzenia związane z dołączaniem i opuszczaniem użytkowników.
8. Konfiguracja
Konfigurowalność: Bot jest skonfigurowany do pracy z określonym serwerem, portem i kanałem, co pozwala na łatwe dostosowanie jego działania do różnych środowisk IRC.
Podsumowując, MemoBot to wszechstronny bot IRC, który zapewnia funkcjonalność zarządzania wiadomościami, alarmami i minutnikami, jednocześnie dbając o utrzymanie aktywnego połączenia z serwerem IRC. Jest to przydatne narzędzie do komunikacji i organizacji zadań na kanałach IRC.
