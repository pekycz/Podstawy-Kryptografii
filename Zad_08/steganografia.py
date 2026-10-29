import random
import secrets


PikselRGB = tuple[int, int, int]
ObrazRGB = list[list[PikselRGB]]
ObrazSzary = list[list[int]]
PikselUdzialu = tuple[bool, bool]


def _sprawdz_obraz_rgb(obraz: ObrazRGB) -> tuple[int, int]:
    """Sprawdza obraz RGB i zwraca jego wymiary."""
    if not obraz or not obraz[0]:
        raise ValueError("Obraz nie może być pusty.")

    szerokosc = len(obraz[0])
    if any(len(wiersz) != szerokosc for wiersz in obraz):
        raise ValueError("Wszystkie wiersze obrazu muszą mieć tę samą długość.")

    # Każdy piksel musi mieć dokładnie trzy składowe RGB z zakresu 0–255.
    for wiersz in obraz:
        for piksel in wiersz:
            if (
                len(piksel) != 3
                or any(not isinstance(kanal, int) or not 0 <= kanal <= 255 for kanal in piksel)
            ):
                raise ValueError("Każdy piksel musi zawierać trzy bajty RGB.")

    return len(obraz), szerokosc


def ukryj_dane(dane: bytes, obraz: ObrazRGB) -> ObrazRGB:
    """Ukrywa dowolne bajty, na przykład tekst albo dane pliku graficznego."""
    wysokosc, szerokosc = _sprawdz_obraz_rgb(obraz)
    if not isinstance(dane, bytes):
        raise TypeError("Ukrywane dane muszą być podane jako bajty.")
    if len(dane) >= 1 << 32:
        raise ValueError("Wiadomość jest za długa, aby zapisać jej rozmiar.")

    # Zapisujemy długość przed treścią, żeby odbiorca wiedział, kiedy zakończyć odczyt.
    zakodowana_wiadomosc = len(dane).to_bytes(4, "big") + dane
    liczba_bitow = len(zakodowana_wiadomosc) * 8
    if liczba_bitow > wysokosc * szerokosc * 3:
        raise ValueError("Obraz jest za mały, aby ukryć w nim tę wiadomość.")

    # Kopia pozwala zachować niezmieniony obraz wejściowy.
    wynik = [[tuple(piksel) for piksel in wiersz] for wiersz in obraz]

    # Bity wiadomości zapisujemy od najbardziej znaczącego do najmniej znaczącego.
    for indeks_bitu in range(liczba_bitow):
        indeks_bajtu, pozycja_bitu = divmod(indeks_bitu, 8)
        bit = (
            zakodowana_wiadomosc[indeks_bajtu]
            >> (7 - pozycja_bitu)
        ) & 1

        # Kolejne bity trafiają do kanałów R, G i B następnych pikseli.
        indeks_piksela, indeks_kanalu = divmod(indeks_bitu, 3)
        y, x = divmod(indeks_piksela, szerokosc)
        piksel = list(wynik[y][x])
        piksel[indeks_kanalu] = (piksel[indeks_kanalu] & 0b11111110) | bit
        wynik[y][x] = tuple(piksel)

    return wynik


def ukryj_wiadomosc(wiadomosc: str, obraz: ObrazRGB) -> ObrazRGB:
    """Koduje tekst jako UTF-8 i ukrywa go w najmłodszych bitach kanałów RGB."""
    return ukryj_dane(wiadomosc.encode("utf-8"), obraz)


def odczytaj_dane(obraz: ObrazRGB) -> bytes:
    """Odczytuje bajty ukryte w najmłodszych bitach kanałów RGB."""
    wysokosc, szerokosc = _sprawdz_obraz_rgb(obraz)
    pojemnosc_bitow = wysokosc * szerokosc * 3

    def odczytaj_bity(poczatek: int, liczba_bitow: int) -> list[int]:
        """Odczytuje wskazany fragment strumienia bitów obrazu."""
        bity: list[int] = []
        for indeks_bitu in range(poczatek, poczatek + liczba_bitow):
            indeks_piksela, indeks_kanalu = divmod(indeks_bitu, 3)
            y, x = divmod(indeks_piksela, szerokosc)
            bity.append(obraz[y][x][indeks_kanalu] & 1)
        return bity

    if pojemnosc_bitow < 32:
        raise ValueError("Obraz jest za mały, aby zawierać nagłówek wiadomości.")

    # Pierwsze 32 bity tworzą czterobajtową długość wiadomości.
    bity_dlugosci = odczytaj_bity(0, 32)
    bajty_dlugosci = bytes(
        sum(bit << (7 - pozycja) for pozycja, bit in enumerate(bity_dlugosci[i : i + 8]))
        for i in range(0, 32, 8)
    )
    dlugosc_wiadomosci = int.from_bytes(bajty_dlugosci, "big")
    liczba_bitow_tresci = dlugosc_wiadomosci * 8
    if 32 + liczba_bitow_tresci > pojemnosc_bitow:
        raise ValueError("Zapisana długość wiadomości przekracza pojemność obrazu.")

    # Odczytujemy dokładnie tyle bitów, ile wskazuje nagłówek, i składamy z nich bajty.
    bity_tresci = odczytaj_bity(32, liczba_bitow_tresci)
    bajty_tresci = bytes(
        sum(bit << (7 - pozycja) for pozycja, bit in enumerate(bity_tresci[i : i + 8]))
        for i in range(0, liczba_bitow_tresci, 8)
    )
    return bajty_tresci


def odczytaj_wiadomosc(obraz: ObrazRGB) -> str:
    """Odczytuje wiadomość tekstową i dekoduje ją z UTF-8."""
    return odczytaj_dane(obraz).decode("utf-8")


def _sprawdz_obraz_szary(obraz: ObrazSzary) -> tuple[int, int]:
    """Sprawdza, czy obraz w skali szarości zawiera wartości 0–255."""
    if not obraz or not obraz[0]:
        raise ValueError("Obraz nie może być pusty.")

    szerokosc = len(obraz[0])
    if any(len(wiersz) != szerokosc for wiersz in obraz):
        raise ValueError("Wszystkie wiersze obrazu muszą mieć tę samą długość.")
    if any(
        not isinstance(jasnosc, int) or not 0 <= jasnosc <= 255
        for wiersz in obraz
        for jasnosc in wiersz
    ):
        raise ValueError("Jasność każdego piksela musi należeć do zakresu 0–255.")

    return len(obraz), szerokosc


def _losuj_pary(
    klucz: str, liczba_iteracji: int, liczba_pikseli: int
) -> list[tuple[int, int]]:
    """Odtwarza te same pseudolosowe pary punktów dla tego samego klucza."""
    if not isinstance(klucz, str) or not klucz:
        raise ValueError("Klucz musi być niepustym tekstem.")
    if liczba_iteracji <= 0:
        raise ValueError("Liczba iteracji musi być większa od zera.")
    if liczba_pikseli < 2:
        raise ValueError("Obraz musi zawierać co najmniej dwa piksele.")

    # Tajny klucz inicjuje generator, dzięki czemu nadawca i odbiorca wybierają te same punkty.
    generator = random.Random(klucz)
    return [
        tuple(generator.sample(range(liczba_pikseli), 2))
        for _ in range(liczba_iteracji)
    ]


def osadz_znak_wodny(
    obraz: ObrazSzary,
    klucz: str,
    liczba_iteracji: int,
    delta: int = 3,
) -> ObrazSzary:
    """Osadza znak Patchwork przez rozjaśnianie i przyciemnianie par pikseli."""
    wysokosc, szerokosc = _sprawdz_obraz_szary(obraz)
    if not 1 <= delta <= 5:
        raise ValueError("Wartość delta musi mieścić się w zakresie od 1 do 5.")

    wynik = [wiersz.copy() for wiersz in obraz]
    pary = _losuj_pary(klucz, liczba_iteracji, wysokosc * szerokosc)

    # Dla każdej wylosowanej pary jeden punkt rozjaśniamy, a drugi przyciemniamy.
    for indeks_a, indeks_b in pary:
        y_a, x_a = divmod(indeks_a, szerokosc)
        y_b, x_b = divmod(indeks_b, szerokosc)
        wynik[y_a][x_a] = min(255, wynik[y_a][x_a] + delta)
        wynik[y_b][x_b] = max(0, wynik[y_b][x_b] - delta)

    return wynik


def wykryj_znak_wodny(
    obraz: ObrazSzary,
    klucz: str,
    liczba_iteracji: int,
    delta: int = 3,
) -> tuple[bool, int]:
    """Wykrywa znak Patchwork i zwraca decyzję wraz z sumą różnic jasności."""
    wysokosc, szerokosc = _sprawdz_obraz_szary(obraz)
    if not 1 <= delta <= 5:
        raise ValueError("Wartość delta musi mieścić się w zakresie od 1 do 5.")

    pary = _losuj_pary(klucz, liczba_iteracji, wysokosc * szerokosc)
    suma_roznic = 0

    # Odtwarzamy pary z klucza i sumujemy różnice jasności w kolejności A minus B.
    for indeks_a, indeks_b in pary:
        y_a, x_a = divmod(indeks_a, szerokosc)
        y_b, x_b = divmod(indeks_b, szerokosc)
        suma_roznic += obraz[y_a][x_a] - obraz[y_b][x_b]

    # Znak przesuwa wynik w okolice 2 * delta * n; połowa tej wartości jest progiem.
    prog = delta * liczba_iteracji
    return suma_roznic > prog, suma_roznic


def wygeneruj_obraz_testowy(wysokosc: int, szerokosc: int) -> ObrazRGB:
    """Tworzy prosty obraz RGB do uruchomienia demonstracji bez dodatkowych bibliotek."""
    return [
        [
            (
                100 + (x * 3 + y) % 40,
                110 + (x + y * 2) % 40,
                120 + (x * 2 + y * 3) % 40,
            )
            for x in range(szerokosc)
        ]
        for y in range(wysokosc)
    ]


def main() -> None:
    print("Laboratorium 8 — steganografia")

    # Wiadomość składa się z nagłówka długości i bajtów UTF-8 zapisanych w obrazie.
    wiadomosc = "Tajna wiadomość"
    obraz_rgb = wygeneruj_obraz_testowy(16, 16)
    obraz_z_wiadomoscia = ukryj_wiadomosc(wiadomosc, obraz_rgb)
    odczytana = odczytaj_wiadomosc(obraz_z_wiadomoscia)
    print("\n1. Najmniej znaczący bit (LSB)")
    print(f"Oryginalna wiadomość: {wiadomosc}")
    print(f"Odczytana wiadomość: {odczytana}")
    print(f"Wiadomości są zgodne: {odczytana == wiadomosc}")

    # Ten sam mechanizm przenosi także bajty pliku graficznego lub innego pliku.
    dane_graficzne = bytes((0x89, 0x50, 0x4E, 0x47, 0x00, 0xFF, 0x10, 0x80))
    obraz_z_danymi = ukryj_dane(dane_graficzne, obraz_rgb)
    print(
        "Odczytane dane binarne są zgodne: "
        f"{odczytaj_dane(obraz_z_danymi) == dane_graficzne}"
    )

    # Piksele mają zapas jasności, żeby osadzanie nie obcinało wartości na granicy 0 lub 255.
    obraz_szary = [
        [100 + (x * 3 + y * 5) % 40 for x in range(32)]
        for y in range(32)
    ]
    klucz = "tajny-klucz-patchwork"
    liczba_iteracji = 100
    delta = 3
    obraz_z_znakiem = osadz_znak_wodny(
        obraz_szary, klucz, liczba_iteracji, delta
    )
    wykryto, suma = wykryj_znak_wodny(
        obraz_z_znakiem, klucz, liczba_iteracji, delta
    )
    print("\n2. Znak wodny Patchwork")
    print(f"Suma różnic jasności: {suma}")
    print(f"Oczekiwana wartość: około {2 * delta * liczba_iteracji}")
    print(f"Znak wodny został wykryty: {wykryto}")

    print(
        "\nDemonstracja korzysta z obrazów w pamięci; "
        "wartości pikseli podawane są w formacie RGB lub skali szarości."
    )


if __name__ == "__main__":
    main()
