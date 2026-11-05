import secrets


def podziel_sekret(sekret, prog, liczba_udzialow, p):
    # Wyraz wolny wielomianu to sekret; pozostałe współczynniki są losowe.
    wspolczynniki = [sekret]
    wspolczynniki += [secrets.randbelow(p) for _ in range(prog - 2)]
    if prog > 1:
        wspolczynniki.append(secrets.randbelow(p - 1) + 1)

    udzialy = []
    for x in range(1, liczba_udzialow + 1):
        y = sum(a * pow(x, i, p) for i, a in enumerate(wspolczynniki)) % p
        udzialy.append((x, y))
    return udzialy


def odtworz_sekret(udzialy, p):
    # Interpolacja Lagrange'a w punkcie x = 0.
    wynik = 0
    for i, (x_i, y_i) in enumerate(udzialy):
        licznik, mianownik = 1, 1
        for j, (x_j, _) in enumerate(udzialy):
            if i != j:
                licznik = licznik * -x_j % p
                mianownik = mianownik * (x_i - x_j) % p
        wynik += y_i * licznik * pow(mianownik, -1, p)
    return wynik % p


def pokaz_obraz(obraz):
    for wiersz in obraz:
        print("".join("#" if piksel else " " for piksel in wiersz))


def main():
    # Dowolne 3 z 5 udziałów wystarczą do odtworzenia sekretu.
    sekret, p = 1234, 2089
    udzialy = podziel_sekret(sekret, prog=3, liczba_udzialow=5, p=p)
    print("Odtworzony sekret:", odtworz_sekret(udzialy[:3], p))

    # Kryptografia wizualna: piksel 0 jest biały, a 1 czarny.
    obraz = [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0]]
    udzial_1, udzial_2 = [], []
    for wiersz in obraz:
        w1, w2 = [], []
        for piksel in wiersz:
            czarny = bool(secrets.randbelow(2))
            pierwszy = (czarny, not czarny)
            drugi = pierwszy if piksel == 0 else (not pierwszy[0], not pierwszy[1])
            w1.append(pierwszy)
            w2.append(drugi)
        udzial_1.append(w1)
        udzial_2.append(w2)

    nalozony = [
        [int(a[0] or b[0]) for a, b in zip(w1, w2)]
        for w1, w2 in zip(udzial_1, udzial_2)
    ]
    print("Obraz po nałożeniu udziałów:")
    pokaz_obraz(nalozony)


if __name__ == "__main__":
    main()
