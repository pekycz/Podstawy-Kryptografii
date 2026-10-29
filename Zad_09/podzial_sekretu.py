import secrets


PikselUdzialu = tuple[bool, bool]


def czy_pierwsza(liczba: int) -> bool:
    """Sprawdza pierwszość liczby metodą próbnego dzielenia."""
    if liczba < 2:
        return False
    if liczba in (2, 3):
        return True
    if liczba % 2 == 0:
        return False

    # Wystarczy sprawdzać dzielniki nie większe niż pierwiastek z liczby.
    dzielnik = 3
    while dzielnik * dzielnik <= liczba:
        if liczba % dzielnik == 0:
            return False
        dzielnik += 2
    return True


def _sprawdz_parametry(sekret: int, prog: int, liczba_udzialow: int, p: int) -> None:
    """Sprawdza parametry potrzebne do obliczeń w ciele modulo p."""
    if not czy_pierwsza(p):
        raise ValueError("Moduł p musi być liczbą pierwszą.")
    if not 0 <= sekret < p:
        raise ValueError("Sekret musi należeć do zakresu od 0 do p - 1.")
    if not 1 <= prog <= liczba_udzialow < p:
        raise ValueError("Parametry muszą spełniać warunek 1 <= próg <= liczba udziałów < p.")


def generuj_udzialy(
    sekret: int, prog: int, liczba_udzialow: int, p: int
) -> list[tuple[int, int]]:
    """Dzieli sekret metodą Shamira i zwraca listę punktów (x, y)."""
    _sprawdz_parametry(sekret, prog, liczba_udzialow, p)

    # Wielomian stopnia prog - 1 ma sekret jako wyraz wolny.
    wspolczynniki = [sekret]
    wspolczynniki.extend(secrets.randbelow(p) for _ in range(prog - 2))
    if prog > 1:
        # Niezerowy współczynnik najwyższej potęgi gwarantuje wymagany stopień wielomianu.
        wspolczynniki.append(secrets.randbelow(p - 1) + 1)

    # Każdy uczestnik otrzymuje wartość wielomianu dla innego, niezerowego x.
    wspolrzedne_x = secrets.SystemRandom().sample(range(1, p), liczba_udzialow)
    udzialy = []
    for x in wspolrzedne_x:
        y = sum(
            wspolczynnik * pow(x, potega, p)
            for potega, wspolczynnik in enumerate(wspolczynniki)
        ) % p
        udzialy.append((x, y))

    return udzialy


def odtworz_sekret(udzialy: list[tuple[int, int]], prog: int, p: int) -> int:
    """Odtwarza sekret interpolacją Lagrange'a w punkcie x = 0."""
    if not czy_pierwsza(p):
        raise ValueError("Moduł p musi być liczbą pierwszą.")
    if not 1 <= prog <= len(udzialy):
        raise ValueError("Do odtworzenia sekretu potrzeba co najmniej tylu udziałów, ile wynosi próg.")

    # Sprawdzamy, czy wszystkie współrzędne są poprawnymi, różnymi elementami pola.
    wspolrzedne_x = [x for x, _ in udzialy]
    if len(set(wspolrzedne_x)) != len(wspolrzedne_x):
        raise ValueError("Udziały muszą mieć różne współrzędne x.")
    if any(not 1 <= x < p or not 0 <= y < p for x, y in udzialy):
        raise ValueError("Współrzędne udziałów muszą należeć do pola modulo p.")

    sekret = 0

    # Każdy punkt wnosi składnik Lagrange'a; w x = 0 licznik to iloczyn -x_j.
    for indeks, (x_i, y_i) in enumerate(udzialy):
        licznik = 1
        mianownik = 1
        for inny_indeks, (x_j, _) in enumerate(udzialy):
            if indeks == inny_indeks:
                continue
            licznik = licznik * (-x_j) % p
            mianownik = mianownik * (x_i - x_j) % p

        # Odwrotność modulo p zastępuje dzielenie w ciele skończonym.
        odwrotnosc_mianownika = pow(mianownik, -1, p)
        wspolczynnik = licznik * odwrotnosc_mianownika % p
        sekret = (sekret + y_i * wspolczynnik) % p

    return sekret


def zaszyfruj_piksel(piksel: int) -> tuple[PikselUdzialu, PikselUdzialu]:
    """Zamienia biały lub czarny piksel na dwa losowe udziały wizualne."""
    if piksel not in (0, 1):
        raise ValueError("Piksel musi mieć wartość 0 (biały) albo 1 (czarny).")

    # Pierwszy udział losowo wybiera, który z dwóch subpikseli będzie czarny.
    pierwszy_czarny = bool(secrets.randbelow(2))
    pierwszy = (pierwszy_czarny, not pierwszy_czarny)

    # Biały piksel używa takiego samego wzoru, a czarny — jego przeciwieństwa.
    if piksel == 0:
        drugi = pierwszy
    else:
        drugi = (not pierwszy[0], not pierwszy[1])
    return pierwszy, drugi

def generuj_udzialy_wizualne(
    obraz: list[list[int]],
) -> tuple[list[list[PikselUdzialu]], list[list[PikselUdzialu]]]:
    """Tworzy dwa udziały obrazu czarno-białego, podwajając szerokość."""
    if not obraz or not obraz[0]:
        raise ValueError("Obraz nie może być pusty.")
    szerokosc = len(obraz[0])
    if any(len(wiersz) != szerokosc for wiersz in obraz):
        raise ValueError("Wszystkie wiersze obrazu muszą mieć tę samą długość.")
    if any(piksel not in (0, 1) for wiersz in obraz for piksel in wiersz):
        raise ValueError("Piksele muszą mieć wartość 0 (biały) albo 1 (czarny).")

    udzial_1 = []
    udzial_2 = []
    for wiersz in obraz:
        wiersz_1 = []
        wiersz_2 = []
        for piksel in wiersz:
            # Każdy piksel wejściowy kodujemy parą subpikseli w obu udziałach.
            pierwszy, drugi = zaszyfruj_piksel(piksel)
            wiersz_1.append(pierwszy)
            wiersz_2.append(drugi)
        udzial_1.append(wiersz_1)
        udzial_2.append(wiersz_2)

    return udzial_1, udzial_2


def naloz_udzialy(
    udzial_1: list[list[PikselUdzialu]],
    udzial_2: list[list[PikselUdzialu]],
) -> list[list[int]]:
    """Nakłada udziały przez OR: czarny wynik pojawia się, gdy czarny jest któryś subpiksel."""
    if not udzial_1 or not udzial_1[0]:
        raise ValueError("Udziały nie mogą być puste.")
    if len(udzial_1) != len(udzial_2):
        raise ValueError("Udziały muszą mieć taką samą wysokość.")

    szerokosc = len(udzial_1[0])
    if szerokosc != len(udzial_2[0]):
        raise ValueError("Udziały muszą mieć taką samą szerokość.")
    if any(len(wiersz) != szerokosc for wiersz in udzial_1 + udzial_2):
        raise ValueError("Wszystkie wiersze udziałów muszą mieć tę samą długość.")

    wynik = []
    for wiersz_1, wiersz_2 in zip(udzial_1, udzial_2):
        wiersz_wynikowy = []
        for piksel_1, piksel_2 in zip(wiersz_1, wiersz_2):
            if len(piksel_1) != 2 or len(piksel_2) != 2:
                raise ValueError("Każdy piksel udziału musi mieć dwa subpiksele.")

            # W druku nałożenie oznacza czerń, jeśli choć jeden subpiksel jest czarny.
            zlozony_1 = piksel_1[0] or piksel_2[0]
            zlozony_2 = piksel_1[1] or piksel_2[1]
            wiersz_wynikowy.extend((int(zlozony_1), int(zlozony_2)))
        wynik.append(wiersz_wynikowy)

    return wynik


def pokaz_obraz(obraz: list[list[int]]) -> None:
    """Wypisuje mały obraz tekstowo, używając # dla czerni."""
    for wiersz in obraz:
        print("".join("#" if piksel else " " for piksel in wiersz))


def main() -> None:
    print("Laboratorium 9 — podział sekretu i kryptografia wizualna")

    # Próg 3 oznacza, że dowolne trzy z pięciu udziałów wystarczą do rekonstrukcji.
    sekret = 1234
    p = 2089
    udzialy = generuj_udzialy(sekret, prog=3, liczba_udzialow=5, p=p)
    odtworzony = odtworz_sekret(udzialy[:3], prog=3, p=p)
    print("\n1. Schemat progowy Shamira")
    print(f"Sekret: {sekret}")
    print(f"Liczba wygenerowanych udziałów: {len(udzialy)}")
    print(f"Sekret odtworzony z trzech udziałów: {odtworzony}")
    print(f"Odtwarzanie zakończone powodzeniem: {odtworzony == sekret}")

    # W obrazie wejściowym 0 oznacza biel, a 1 czerń.
    obraz = [
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 0],
    ]
    udzial_1, udzial_2 = generuj_udzialy_wizualne(obraz)
    obraz_odtworzony = naloz_udzialy(udzial_1, udzial_2)
    print("\n2. Kryptografia wizualna")
    print("Oryginalny obraz (# oznacza piksel czarny):")
    pokaz_obraz(obraz)
    print("Obraz po nałożeniu obu udziałów (każdy piksel ma dwa subpiksele):")
    pokaz_obraz(obraz_odtworzony)


if __name__ == "__main__":
    main()
