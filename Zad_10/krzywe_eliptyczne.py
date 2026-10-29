import math
import secrets
from typing import TypeAlias


# Parametry przykładowej krzywej: y^2 = x^3 + ax + b (mod p).
P = 97
A = 2
B = 3
PUNKT_BAZOWY = (3, 6)

Punkt: TypeAlias = tuple[int, int] | None


def czy_na_krzywej(punkt: Punkt) -> bool:
    """Sprawdza, czy punkt spełnia równanie krzywej nad polem modulo P."""
    if punkt is None:
        # Punkt w nieskończoności jest elementem neutralnym dodawania punktów.
        return True

    x, y = punkt
    if not 0 <= x < P or not 0 <= y < P:
        return False
    return (y * y - (x * x * x + A * x + B)) % P == 0


def dodaj_punkty(punkt_1: Punkt, punkt_2: Punkt) -> Punkt:
    """Dodaje punkty na krzywej eliptycznej zgodnie ze wzorami modulo P."""
    if not czy_na_krzywej(punkt_1) or not czy_na_krzywej(punkt_2):
        raise ValueError("Oba argumenty muszą leżeć na zadanej krzywej.")

    # Punkt w nieskończoności nie zmienia drugiego argumentu.
    if punkt_1 is None:
        return punkt_2
    if punkt_2 is None:
        return punkt_1

    x_1, y_1 = punkt_1
    x_2, y_2 = punkt_2

    # Punkt i jego odbicie względem osi x sumują się do punktu w nieskończoności.
    if x_1 == x_2 and (y_1 + y_2) % P == 0:
        return None

    if punkt_1 == punkt_2:
        # Przy podwajaniu nachylenie wykorzystuje pochodną prawej strony krzywej.
        licznik = (3 * x_1 * x_1 + A) % P
        mianownik = (2 * y_1) % P
    else:
        # Dla różnych punktów nachylenie jest ilorazem różnic współrzędnych.
        licznik = (y_2 - y_1) % P
        mianownik = (x_2 - x_1) % P

    if mianownik == 0:
        return None

    # W ciele modulo p dzielenie zastępujemy mnożeniem przez odwrotność modulo p.
    nachylenie = licznik * pow(mianownik, -1, P) % P
    x_wynikowy = (nachylenie * nachylenie - x_1 - x_2) % P
    y_wynikowy = (nachylenie * (x_1 - x_wynikowy) - y_1) % P
    return x_wynikowy, y_wynikowy


def pomnoz_punkt(punkt: Punkt, skalar: int) -> Punkt:
    """Oblicza wielokrotność punktu algorytmem double-and-add."""
    if not czy_na_krzywej(punkt):
        raise ValueError("Punkt musi leżeć na zadanej krzywej.")
    if skalar < 0:
        raise ValueError("Skalar nie może być ujemny.")

    wynik: Punkt = None
    aktualny_punkt = punkt
    pozostaly_skalar = skalar

    # Każdy bit skalara decyduje, czy dodajemy aktualną wielokrotność punktu.
    while pozostaly_skalar:
        if pozostaly_skalar & 1:
            wynik = dodaj_punkty(wynik, aktualny_punkt)

        # Podwajamy punkt i przechodzimy do następnego bitu skalara.
        aktualny_punkt = dodaj_punkty(aktualny_punkt, aktualny_punkt)
        pozostaly_skalar >>= 1

    return wynik


def oblicz_rzad_punktu(punkt: Punkt) -> int:
    """Wyznacza najmniejszą dodatnią wielokrotność punktu równą punktowi w nieskończoności."""
    if punkt is None or not czy_na_krzywej(punkt):
        raise ValueError("Należy podać poprawny, niezerowy punkt krzywej.")

    # Twierdzenie Hassego ogranicza rząd grupy, więc w tym zakresie znajdziemy rząd punktu.
    maksymalny_rzad = P + 1 + math.isqrt(4 * P)
    for rzad in range(1, maksymalny_rzad + 1):
        if pomnoz_punkt(punkt, rzad) is None:
            return rzad
    raise RuntimeError("Nie udało się wyznaczyć rzędu punktu bazowego.")


def przeprowadz_wymiane_ecdh() -> tuple[Punkt, Punkt, bool]:
    """Przeprowadza wymianę klucza Diffiego-Hellmana na krzywej eliptycznej."""
    rzad_punktu = oblicz_rzad_punktu(PUNKT_BAZOWY)
    if rzad_punktu < 2:
        raise ValueError("Punkt bazowy musi mieć rząd co najmniej 2.")

    # Prywatne skalary losujemy z zakresu od 1 do rzędu punktu bazowego minus 1.
    klucz_prywatny_a = secrets.randbelow(rzad_punktu - 1) + 1
    klucz_prywatny_b = secrets.randbelow(rzad_punktu - 1) + 1

    # Każda strona mnoży jawny punkt bazowy przez swój prywatny skalar.
    klucz_publiczny_a = pomnoz_punkt(PUNKT_BAZOWY, klucz_prywatny_a)
    klucz_publiczny_b = pomnoz_punkt(PUNKT_BAZOWY, klucz_prywatny_b)

    # Każda strona mnoży punkt drugiej strony przez własny prywatny skalar.
    sekret_a = pomnoz_punkt(klucz_publiczny_b, klucz_prywatny_a)
    sekret_b = pomnoz_punkt(klucz_publiczny_a, klucz_prywatny_b)
    return sekret_a, sekret_b, sekret_a == sekret_b


def main() -> None:
    print("Laboratorium 10 — krzywe eliptyczne")
    print(f"Krzywa: y^2 = x^3 + {A}x + {B} (mod {P})")
    print(f"Punkt bazowy G: {PUNKT_BAZOWY}")
    print(f"Punkt bazowy leży na krzywej: {czy_na_krzywej(PUNKT_BAZOWY)}")
    print(
        "Rząd G (najmniejsze n, dla którego nG jest punktem w nieskończoności): "
        f"{oblicz_rzad_punktu(PUNKT_BAZOWY)}"
    )
    print(f"2G: {pomnoz_punkt(PUNKT_BAZOWY, 2)}")
    print(f"3G: {pomnoz_punkt(PUNKT_BAZOWY, 3)}")

    sekret_a, sekret_b, zgodne = przeprowadz_wymiane_ecdh()
    print("\nWymiana klucza ECDH")
    print(f"Wspólny punkt obliczony przez A: {sekret_a}")
    print(f"Wspólny punkt obliczony przez B: {sekret_b}")
    print(f"Sekrety obu stron są zgodne: {zgodne}")
    print(
        "\nUwaga: parametry p = 97 i punkt bazowy z zadania są edukacyjne "
        "i nie zapewniają bezpieczeństwa kryptograficznego."
    )


if __name__ == "__main__":
    main()
