import secrets


# N - Bezpieczna liczba pierwsza(2048 bitów) i G - jej pierwiastek pierwotny modulo.
N = 32317006071311007300338913926423828248817941241140239112842009751400741706634354222619689417363569347117901737909704191754605873209195028853758986185622153212175412514901774520270235796078236248884246189477587641105928646099411723245426622522193230540919037680524235519125679715870117001058055877651038861847280257976054903569732561526167081339361799541336476559160368317896729073178384589680639671900977202194168647225871031411336429319536193471636533209717077448227988588565369208645296636077250268955505928362751121174096972998068410554359584866583291642136218231078990999448652468262416972035911852507045361090559
G = 11


def generuj_klucz_prywatny() -> int:
    #Losuje prywatny wykładnik z zakresu od 2 do N-2.
    return secrets.randbelow(N - 3) + 2


def oblicz_klucz_publiczny(klucz_prywatny: int) -> int:
    #Oblicza G^klucz_prywatny modulo N.
    return pow(G, klucz_prywatny, N)


def oblicz_sekret(wartosc_publiczna: int, klucz_prywatny: int) -> int:
    #Oblicza wspólną wartość po otrzymaniu klucza publicznego drugiej strony.
    return pow(wartosc_publiczna, klucz_prywatny, N)


def pokaz_sekret(nazwa: str, sekret: int) -> None:
    print(f"{nazwa}: {sekret:0{(N.bit_length() + 3) // 4}x}")


def wymiana_dh() -> None:
    # Dla tej bezpiecznej liczby pierwszej (N-1 = 2Q, Q pierwsze)
    # G=11 jest pierwiastkiem pierwotnym modulo N.
    assert pow(G, 2, N) != 1 and pow(G, (N - 1) // 2, N) == N - 1

    klucz_a = generuj_klucz_prywatny()
    klucz_b = generuj_klucz_prywatny()
    publiczny_a = oblicz_klucz_publiczny(klucz_a)
    publiczny_b = oblicz_klucz_publiczny(klucz_b)

    sekret_a = oblicz_sekret(publiczny_b, klucz_a)
    sekret_b = oblicz_sekret(publiczny_a, klucz_b)

    print("Zwykła wymiana Diffiego-Hellmana")
    print(f"N: {N.bit_length()}-bitowa liczba pierwsza")
    print(f"G: {G}")
    print(f"Wartość publiczna A: {publiczny_a:x}")
    print(f"Wartość publiczna B: {publiczny_b:x}")
    pokaz_sekret("Sekret A", sekret_a)
    pokaz_sekret("Sekret B", sekret_b)
    print(f"Sekrety są takie same: {sekret_a == sekret_b}")


def symuluj_mitm() -> None:
    # Bez uwierzytelnienia A i B nie wiedzą, kto wysłał otrzymaną wartość.
    klucz_a = generuj_klucz_prywatny()
    klucz_b = generuj_klucz_prywatny()
    klucz_e = generuj_klucz_prywatny()
    publiczny_a = oblicz_klucz_publiczny(klucz_a)
    publiczny_b = oblicz_klucz_publiczny(klucz_b)
    publiczny_e = oblicz_klucz_publiczny(klucz_e)

    # E przechwytuje X i Y, po czym zamiast nich wysyła A i B własne Z.
    sekret_a = oblicz_sekret(publiczny_e, klucz_a)
    sekret_b = oblicz_sekret(publiczny_e, klucz_b)

    # E oblicza osobny sekret z każdą stroną, używając przechwyconych wartości.
    sekret_e_a = oblicz_sekret(publiczny_a, klucz_e)
    sekret_e_b = oblicz_sekret(publiczny_b, klucz_e)

    assert sekret_a == sekret_e_a
    assert sekret_b == sekret_e_b

    print("\nSymulacja ataku Man-in-the-Middle")
    print(f"E podmienia wartości publiczne A i B na Z: {publiczny_e:x}")
    print(f"A i E mają ten sam sekret: {sekret_a == sekret_e_a}")
    print(f"B i E mają ten sam sekret: {sekret_b == sekret_e_b}")
    print(f"A i B mają ten sam sekret: {sekret_a == sekret_b}")
    pokaz_sekret("Sekret współdzielony przez A i E", sekret_e_a)
    pokaz_sekret("Sekret współdzielony przez B i E", sekret_e_b)


if __name__ == "__main__":
    wymiana_dh()
    symuluj_mitm()

