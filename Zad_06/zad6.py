import math
import secrets
from collections.abc import Iterator


ROZMIAR_PRIME_BITS = 1024
LICZBA_RUND_MILLERA_RABINA = 40
WYKLADNIK_PUBLICZNY = 65537


def czy_prawdopodobnie_pierwsza(liczba: int) -> bool:
    """Testuje pierwszość liczby testem Millera-Rabina."""
    male_pierwsze = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if liczba < 2:
        return False
    if liczba in male_pierwsze:
        return True
    if any(liczba % dzielnik == 0 for dzielnik in male_pierwsze):
        return False

    # Rozkładamy liczba - 1 na 2^s * d, gdzie d jest nieparzyste.
    d = liczba - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    # Losowe podstawy testu zmniejszają prawdopodobieństwo błędnej klasyfikacji.
    for _ in range(LICZBA_RUND_MILLERA_RABINA):
        podstawa = secrets.randbelow(liczba - 3) + 2
        wynik = pow(podstawa, d, liczba)
        if wynik in (1, liczba - 1):
            continue
        for _ in range(s - 1):
            wynik = pow(wynik, 2, liczba)
            if wynik == liczba - 1:
                break
        else:
            return False
    return True


def generuj_liczbe_pierwsza(liczba_bitow: int) -> int:
    """Generuje nieparzystą liczbę o wskazanej długości bitowej."""
    while True:
        kandydat = secrets.randbits(liczba_bitow)
        kandydat |= (1 << (liczba_bitow - 1)) | 1 #dwa bity ustawione na 1, aby zapewnić odpowiednią długość i nieparzystość
        if czy_prawdopodobnie_pierwsza(kandydat):
            return kandydat


def generuj_klucze() -> tuple[tuple[int, int], tuple[int, int]]:
    """Zwraca klucz publiczny (N, e) i prywatny (N, d)."""
    while True:
        p = generuj_liczbe_pierwsza(ROZMIAR_PRIME_BITS)
        q = generuj_liczbe_pierwsza(ROZMIAR_PRIME_BITS)
        if p == q:
            continue

        n = p * q
        if n.bit_length() != 2 * ROZMIAR_PRIME_BITS:
            continue
        phi = (p - 1) * (q - 1)
        e = WYKLADNIK_PUBLICZNY
        if math.gcd(e, phi) == 1:
            d = pow(e, -1, phi)
            return (n, e), (n, d)


def szyfruj(wiadomosc: int, klucz_publiczny: tuple[int, int]) -> int:
    """Szyfruje nieujemną liczbę mniejszą od N bez paddingu (wariant edukacyjny)."""
    n, e = klucz_publiczny
    if not 0 <= wiadomosc < n:
        raise ValueError("Wiadomość musi być liczbą z zakresu 0 <= M < N.")
    return pow(wiadomosc, e, n)


def deszyfruj(szyfrogram: int, klucz_prywatny: tuple[int, int]) -> int:
    """Odszyfrowuje szyfrogram mniejszy od N (wariant edukacyjny bez paddingu)."""
    n, d = klucz_prywatny
    if not 0 <= szyfrogram < n:
        raise ValueError("Szyfrogram musi być liczbą z zakresu 0 <= C < N.")
    return pow(szyfrogram, d, n)


def generuj_bity_rsa(
    klucz_publiczny: tuple[int, int],
    liczba_bitow: int,
    ziarno: int | None = None,
) -> Iterator[int]:
    """Zwraca najmłodszy bit kolejnych stanów generatora RSA."""
    n, e = klucz_publiczny
    if n <= 3 or e <= 0:
        raise ValueError("Nieprawidłowy klucz publiczny.")
    if liczba_bitow < 0:
        raise ValueError("Liczba bitów nie może być ujemna.")
    if ziarno is None:
        ziarno = secrets.randbelow(n - 2) + 2
    if not 1 < ziarno < n:
        raise ValueError("Ziarno musi spełniać warunek 1 < x0 < N.")

    stan = ziarno
    for _ in range(liczba_bitow):
        stan = pow(stan, e, n)
        yield stan & 1


def main() -> None:
    klucz_publiczny, klucz_prywatny = generuj_klucze()
    n, e = klucz_publiczny
    wiadomosc = "Ala ma kota".encode("utf-8")
    liczba_jawna = int.from_bytes(wiadomosc, "big")
    szyfrogram = szyfruj(liczba_jawna, klucz_publiczny)
    odszyfrowana = deszyfruj(szyfrogram, klucz_prywatny)
    odzyskane_bajty = odszyfrowana.to_bytes(len(wiadomosc), "big")

    # Generator jest pokazany edukacyjnie; nie należy używać go do prawdziwych kluczy.
    ciag_bitow = "".join(str(bit) for bit in generuj_bity_rsa(klucz_publiczny, 64))

    print("RSA — demonstracja")
    print(f"Długość N: {n.bit_length()} bitów")
    print(f"Wykładnik publiczny e: {e}")
    print(f"Wiadomość: {wiadomosc.decode('utf-8')}")
    print(f"Szyfrogram: {szyfrogram:x}")
    print(f"Odszyfrowana wiadomość: {odzyskane_bajty.decode('utf-8')}")
    print(f"Poprawne odszyfrowanie: {odzyskane_bajty == wiadomosc}")
    print(f"64 bity generatora RSA: {ciag_bitow}")


if __name__ == "__main__":
    main()
