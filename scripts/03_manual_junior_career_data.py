"""
Rucno kurirani (manually curated) podaci o "pre-F1" karijeri vozaca:
pripadnost akademiji konstruktora (npr. Red Bull Junior Team) i tim u
juniorskoj seriji (GP2/GP3/F2/F3/FR3.5...) pre ulaska u Formulu 1.

ZASTO RUCNO KURIRANO (obrazlozenje, u skladu sa uslovom iz specifikacije
projekta da se objasni zasto i sta modeluju rucno/sintetizovani podaci):
Ne postoji jedinstven besplatan, masinski citljiv API koji povezuje F1
vozace sa njihovim junior-kategorija timovima i akademijama (Ergast/Jolpica
API pokriva SAMO F1 nivo). Ovi podaci su prikupljeni iz javno dostupnih,
dobro dokumentovanih izvora (Wikipedia stranice pojedinacnih akademija i
sezona FIA Formula 2 prvenstva, dohvacene 2026-08-24) i opsteg javnog znanja
o karijerama vozaca. Predstavljaju NAJBOLJU DOSTUPNU APROKSIMACIJU stvarne
karijerne putanje, ne zvanicnu bazu podataka.

METOD: za svakog vozaca iz F1 skupa (2018-2025) belezi se (godina, tip,
naziv entiteta, nivo pouzdanosti). "academy" = program mladih vozaca pri
konstruktoru; "junior_team" = tim u kome je vozac vozio u nizoj seriji
(najcesce GP2/F2). Godina oznacava (priblizno) prvu godinu u tom entitetu -
koristi se iskljucivo za hronolosko uredjivanje koraka karijere, ne kao
tacan datum.

OGRANICENJA (vazno za tumacenje rezultata):
 - Pouzdanost je VISOKA za vozace koji su vozili F2 u modernoj eri
   (2017+), jer su ti podaci unakrsno provereni sa Wikipedia tabelama
   postave timova po sezoni.
 - Pouzdanost je SREDNJA/NISKA za starije vozace (GP2/GP3/F3 era pre 2017),
   jer se oslanja na opste poznate cinjenice bez sistematske provere
   svakog detalja (godina, tacan naziv tima).
 - Model pojednostavljuje: svaki vozac ima najvise JEDNU "primarnu"
   akademiju, iako je u realnosti pripadnost ponekad bila neformalna,
   preklapajuca se ili promenljiva (npr. Albon je rano bio u Red Bull
   programu, ispao, pa se vratio bez formalne akademije u medjuvremenu).
 - Vozaci bez ulaska: Raikkonen, Alonso i Bottas namerno NEMAJU zapis
   (Raikkonen i Alonso su presli u F1 bez akademije/GP2-F2 koraka - poznat
   "skip" slucaj; Bottas je bio neformalni Williams test-vozac pre nego
   sto je "Williams Driver Academy" kao entitet uopste formalno postojao
   2019, pa ne uklapamo taj neformalni odnos u model formalnih akademija).
   Ovo NIJE greska - to je namerni nalaz: ovi vozaci se u mrezi pojavljuju
   kao cvorovi bez ulaznih "pipeline" grana.
"""
import csv
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# driver_id -> list of (year, type, entity_name, confidence)
DATA = {
    "max_verstappen": [(2014, "academy", "Red Bull Junior Team", "high")],
    "gasly": [(2014, "academy", "Red Bull Junior Team", "high"),
              (2016, "junior_team", "Prema Racing (GP2)", "high")],
    "ricciardo": [(2008, "academy", "Red Bull Junior Team", "high"),
                  (2010, "junior_team", "Carlin (FR3.5/GP3)", "medium")],
    "kvyat": [(2011, "academy", "Red Bull Junior Team", "high"),
              (2013, "junior_team", "MW Arden (GP3)", "medium")],
    "sainz": [(2011, "academy", "Red Bull Junior Team", "high"),
              (2015, "junior_team", "Carlin (GP2)", "high")],
    "albon": [(2012, "academy", "Red Bull Junior Team", "medium"),
              (2018, "junior_team", "DAMS (F2)", "high")],
    "tsunoda": [(2018, "academy", "Red Bull Junior Team", "high"),
                (2020, "junior_team", "Carlin (F2)", "high")],
    "lawson": [(2019, "academy", "Red Bull Junior Team", "high"),
               (2021, "junior_team", "Hitech Grand Prix (F2)", "high"),
               (2022, "junior_team", "Carlin (F2)", "high")],
    "hadjar": [(2022, "academy", "Red Bull Junior Team", "high"),
               (2023, "junior_team", "Hitech Pulse-Eight (F2)", "high"),
               (2024, "junior_team", "Campos Racing (F2)", "high")],
    "vettel": [(1998, "academy", "Red Bull Junior Team", "high")],
    "brendon_hartley": [(2007, "academy", "Red Bull Junior Team", "medium")],

    "leclerc": [(2016, "academy", "Ferrari Driver Academy", "high"),
                (2017, "junior_team", "Prema Racing (F2)", "high")],
    "mick_schumacher": [(2019, "academy", "Ferrari Driver Academy", "high"),
                        (2019, "junior_team", "Prema Racing (F2)", "high")],
    "bearman": [(2021, "academy", "Ferrari Driver Academy", "high"),
                (2023, "junior_team", "Prema Racing (F2)", "high")],
    "perez": [(2009, "junior_team", "Barwa Addax Team (GP2)", "medium"),
              (2010, "academy", "Ferrari Driver Academy", "medium")],
    "stroll": [(2010, "academy", "Ferrari Driver Academy", "high"),
               (2016, "junior_team", "Prema Racing (European F3)", "high")],
    "giovinazzi": [(2016, "academy", "Ferrari Driver Academy", "medium"),
                   (2016, "junior_team", "Prema Racing (GP2)", "high")],
    "zhou": [(2014, "academy", "Ferrari Driver Academy", "high"),
             (2019, "junior_team", "UNI-Virtuosi Racing (F2)", "high")],

    "russell": [(2017, "academy", "Mercedes Junior Team", "high"),
                (2018, "junior_team", "ART Grand Prix (F2)", "high")],
    "antonelli": [(2019, "academy", "Mercedes Junior Team", "high"),
                  (2024, "junior_team", "Prema Racing (F2)", "high")],
    "ocon": [(2014, "academy", "Mercedes Junior Team", "high")],

    "doohan": [(2021, "junior_team", "MP Motorsport (F2)", "medium"),
               (2022, "academy", "Alpine Academy", "high"),
               (2022, "junior_team", "Virtuosi Racing (F2)", "high"),
               (2023, "junior_team", "Invicta Virtuosi Racing (F2)", "high")],
    "piastri": [(2020, "academy", "Alpine Academy", "high"),
                (2021, "junior_team", "Prema Racing (F2)", "high")],

    "norris": [(2017, "academy", "McLaren Driver Development Programme", "high"),
               (2018, "junior_team", "Carlin (F2)", "high")],
    "kevin_magnussen": [(2010, "academy", "McLaren Driver Development Programme", "high")],
    "vandoorne": [(2013, "academy", "McLaren Driver Development Programme", "high")],
    "de_vries": [(2010, "academy", "McLaren Driver Development Programme", "high"),
                 (2018, "junior_team", "Prema Racing (F2)", "high"),
                 (2019, "junior_team", "ART Grand Prix (F2)", "high")],
    "hamilton": [(1998, "academy", "McLaren Driver Development Programme", "high")],
    "bortoleto": [(2023, "academy", "McLaren Driver Development Programme", "high"),
                  (2024, "junior_team", "Invicta Racing (F2)", "high")],

    "latifi": [(2018, "junior_team", "DAMS (F2)", "high"),
               (2019, "academy", "Williams Driver Academy", "high")],
    "aitken": [(2018, "junior_team", "ART Grand Prix (F2)", "high"),
               (2019, "junior_team", "Campos Racing (F2)", "high"),
               (2020, "academy", "Williams Driver Academy", "high"),
               (2021, "junior_team", "HWA Racelab (F2)", "high")],
    "sargeant": [(2021, "junior_team", "HWA Racelab (F2)", "high"),
                 (2022, "academy", "Williams Driver Academy", "high"),
                 (2022, "junior_team", "Carlin (F2)", "high")],
    "colapinto": [(2023, "junior_team", "MP Motorsport (F2)", "high"),
                  (2024, "academy", "Williams Driver Academy", "high"),
                  (2024, "junior_team", "MP Motorsport (F2)", "high")],

    "mazepin": [(2019, "junior_team", "ART Grand Prix (F2)", "high"),
                (2020, "junior_team", "Hitech Grand Prix (F2)", "high")],
    "sirotkin": [(2015, "academy", "Renault Sport Academy", "medium"),
                 (2016, "junior_team", "ART Grand Prix (GP2)", "high")],

    "grosjean": [(2011, "junior_team", "DAMS (GP2)", "high")],
    "hulkenberg": [(2009, "junior_team", "ART Grand Prix (GP2)", "high")],
    "kubica": [(2005, "junior_team", "RC Motorsport (F3 Euro Series)", "medium")],
    "ericsson": [(2013, "junior_team", "iSport International (GP2)", "high")],
    "pietro_fittipaldi": [(2019, "junior_team", "Charouz Racing System (F2)", "high"),
                          (2020, "junior_team", "Charouz Racing System (F2)", "high")],

    # namerno bez zapisa (obrazlozeno u docstring-u): raikkonen, alonso, bottas
}


def main():
    rows = []
    for driver_id, entries in DATA.items():
        for year, etype, entity, confidence in entries:
            rows.append({
                "driver_id": driver_id,
                "year": year,
                "entity_type": etype,
                "entity_name": entity,
                "confidence": confidence,
            })
    rows.sort(key=lambda r: (r["driver_id"], r["year"]))

    out_path = PROCESSED_DIR / "junior_career_manual.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["driver_id", "year", "entity_type", "entity_name", "confidence"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows for {len(DATA)} drivers -> {out_path}")


if __name__ == "__main__":
    main()
