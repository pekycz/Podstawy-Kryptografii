import secrets


# Bezpieczna liczba pierwsza z grupy 14 RFC 3526 (2048 bitów).
N = int(
    """
    FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1
    29024E088A67CC74020BBEA63B139B22514A08798E3404DD
    EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245
    E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED
    EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D
    C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F
    83655D23DCA3AD961C62F356208552BB9ED529077096966D
    670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B
    E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9
    DE2BCBF6955817183995497CEA956AE515D2261898FA0510
    15728E5A8AACAA68FFFFFFFFFFFFFFFF
    """.replace("\n", "").replace(" ", ""),
    16,
)
G = 11


def generuj_klucz_prywatny() -> int:
    """Losuje prywatny wykładnik z zakresu od 2 do N-2."""
    return secrets.randbelow(N - 3) + 2


def oblicz_klucz_publiczny(klucz_prywatny: int) -> int:
    """Oblicza G^klucz_prywatny modulo N."""
    return pow(G, klucz_prywatny, N)


def oblicz_sekret(wartosc_publiczna: int, klucz_prywatny: int) -> int:
    """Oblicza wspólną wartość po otrzymaniu klucza publicznego drugiej strony."""
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