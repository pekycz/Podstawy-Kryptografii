import hashlib
import math
import secrets


def czy_prawdopodobnie_pierwsza(n):
    if n < 2 or n % 2 == 0:
        return n == 2
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(20):
        x = pow(secrets.randbelow(n - 3) + 2, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generuj_klucze():
    e = 65537
    while True:
        p, q = (secrets.randbits(512) | (1 << 511) | 1 for _ in range(2))
        while not czy_prawdopodobnie_pierwsza(p):
            p = secrets.randbits(512) | (1 << 511) | 1
        while not czy_prawdopodobnie_pierwsza(q) or q == p:
            q = secrets.randbits(512) | (1 << 511) | 1
        n = p * q
        phi = (p - 1) * (q - 1)
        if n.bit_length() == 1024 and math.gcd(e, phi) == 1:
            return n, e, pow(e, -1, phi)


def podpisz_skrot(wiadomosc, n, d):
    skrot = int.from_bytes(hashlib.sha256(wiadomosc).digest(), "big")
    return pow(skrot, d, n)


def sprawdz_podpis(podpis, wiadomosc, n, e):
    skrot = int.from_bytes(hashlib.sha256(wiadomosc).digest(), "big")
    return pow(podpis, e, n) == skrot


def main():
    # Krótka demonstracja używa surowego RSA, bez bezpiecznego paddingu.
    n, e, d = generuj_klucze()

    wiadomosc = b"Tomek ma kota"
    liczba = int.from_bytes(wiadomosc, "big")
    podpis = pow(liczba, d, n)
    print("Podpis wiadomości jest poprawny:", pow(podpis, e, n) == liczba)

    # Bez paddingu można wybrać podpis, a pasującą wiadomość obliczyć kluczem publicznym.
    falszywy_podpis = secrets.randbelow(n - 1) + 1
    falszywa_wiadomosc = pow(falszywy_podpis, e, n)
    print("Fałszywa para przechodzi weryfikację:",
          pow(falszywy_podpis, e, n) == falszywa_wiadomosc)

    # Naiwne RSA jest homomorficzne: podpisy 2 i 3 dają podpis liczby 6.
    podpis_iloczynu = pow(2, d, n) * pow(3, d, n) % n
    print("Połączone podpisy potwierdzają 6:",
          pow(podpis_iloczynu, e, n) == 6)

    podpis = podpisz_skrot(wiadomosc, n, d)
    print("\nPodpis skrótu SHA-256 jest poprawny:",
          sprawdz_podpis(podpis, wiadomosc, n, e))
    print("Podpis nie pasuje do zmienionej wiadomości:",
          not sprawdz_podpis(podpis, b"Inna wiadomosc", n, e))

    # Próba ataku homomorficznego na podpisach skrótów wiadomości 2 i 3.
    podpis_2 = podpisz_skrot(b"2", n, d)
    podpis_3 = podpisz_skrot(b"3", n, d)
    polaczony_podpis = podpis_2 * podpis_3 % n
    print("Połączone podpisy potwierdzają wiadomość 6:",
          sprawdz_podpis(polaczony_podpis, b"6", n, e))


if __name__ == "__main__":
    main()
