import hashlib
import time

wiadomosci = ["A" * dlugosc for dlugosc in (11, 100, 1_000, 10_000, 100_000)]
metody = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
]

for wiadomosc in wiadomosci:
    powtorzenia = max(1, 100_000 // len(wiadomosc))
    print(f"\nDługość wiadomości: {len(wiadomosc.encode('utf-8'))} bajtów")
    for metoda in metody:
        poczatek = time.perf_counter()
        for _ in range(powtorzenia):
            skrot = hashlib.new(metoda, wiadomosc.encode("utf-8")).hexdigest()
        czas_ms = (time.perf_counter() - poczatek) * 1000
        print(f"{metoda:9} {skrot}  {czas_ms:.3f} ms")
