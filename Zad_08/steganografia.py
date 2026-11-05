import random


def ukryj_wiadomosc(wiadomosc, obraz):
    bity = "".join(f"{bajt:08b}" for bajt in wiadomosc.encode("utf-8"))
    wysokosc, szerokosc = len(obraz), len(obraz[0])
    if len(bity) > wysokosc * szerokosc * 3:
        raise ValueError("Obraz jest za mały.")

    wynik = [[piksel.copy() for piksel in wiersz] for wiersz in obraz]
    for i, bit in enumerate(bity):
        y, x = divmod(i // 3, szerokosc)
        kanal = i % 3
        wynik[y][x][kanal] = (wynik[y][x][kanal] & 254) | int(bit)
    return wynik


def odczytaj_wiadomosc(obraz, liczba_bajtow):
    wysokosc, szerokosc = len(obraz), len(obraz[0])
    bity = []
    for i in range(liczba_bajtow * 8):
        y, x = divmod(i // 3, szerokosc)
        bity.append(str(obraz[y][x][i % 3] & 1))
    tekst = "".join(bity)
    return bytes(int(tekst[i:i + 8], 2) for i in range(0, len(tekst), 8)).decode("utf-8")


def main():
    # LSB: zapisujemy tekst w najmłodszych bitach składowych RGB.
    obraz = [[[128, 128, 128] for _ in range(16)] for _ in range(16)]
    wiadomosc = "Tajna wiadomosc"
    ukryty = ukryj_wiadomosc(wiadomosc, obraz)
    print("Odczytany tekst:", odczytaj_wiadomosc(ukryty, len(wiadomosc.encode("utf-8"))))

    # Patchwork: rozjaśniamy i przyciemniamy wylosowane pary pikseli.
    szary = [128] * 100
    klucz, iteracje, delta = "klucz", 50, 3
    generator = random.Random(klucz)
    pary = [generator.sample(range(len(szary)), 2) for _ in range(iteracje)]
    znak = szary.copy()
    for a, b in pary:
        znak[a] += delta
        znak[b] -= delta

    suma = sum(znak[a] - znak[b] for a, b in pary)
    print("Znak wodny wykryty:", suma > delta * iteracje)


if __name__ == "__main__":
    main()
