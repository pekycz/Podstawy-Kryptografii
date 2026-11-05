import secrets


# Krzywa y^2 = x^3 + ax + b (mod p);
p, a, b = 97, 2, 3
G = (3, 6)


def dodaj(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P == Q:
        nachylenie = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        nachylenie = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (nachylenie**2 - x1 - x2) % p
    y3 = (nachylenie * (x1 - x3) - y1) % p
    return x3, y3


def pomnoz(P, n):
    wynik = None
    while n:
        if n & 1:
            wynik = dodaj(wynik, P)
        P = dodaj(P, P)
        n >>= 1
    return wynik


def main():
    # Znajdujemy rząd punktu bazowego, aby wylosować niezerowe klucze prywatne.
    rzad = next(n for n in range(1, 120) if pomnoz(G, n) is None)
    klucz_a = secrets.randbelow(rzad - 1) + 1
    klucz_b = secrets.randbelow(rzad - 1) + 1

    publiczny_a = pomnoz(G, klucz_a)
    publiczny_b = pomnoz(G, klucz_b)
    sekret_a = pomnoz(publiczny_b, klucz_a)
    sekret_b = pomnoz(publiczny_a, klucz_b)

    print("Punkt bazowy G:", G)
    print("Wspólny sekret A:", sekret_a)
    print("Wspólny sekret B:", sekret_b)
    print("Sekrety są zgodne:", sekret_a == sekret_b)
    print("Uwaga: te małe parametry nie są bezpieczne w praktyce.")


if __name__ == "__main__":
    main()
