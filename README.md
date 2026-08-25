# Analiza mreže transfera vozača Formule 1

Projekat za predmet Analiza društvenih mreža — identifikacija akademija,
feeder timova i ključnih aktera u mreži karijernih prelaza vozača F1
(2018-2025).

Finalni izveštaj: `report/izvestaj.pdf`

## Struktura

```
scripts/
  01_fetch_f1_data.py           preuzimanje sirovih F1 rezultata (Jolpica API)
  02_parse_f1_results.py        parsiranje/čišćenje u data/processed/f1_race_results_2018_2025.csv
  03_manual_junior_career_data.py  ručno kurirani podaci o akademijama/junior timovima
  04_build_network.py           gradnja mreže (čvorovi/grane)
  05_eda.py                     eksplorativna analiza + preliminarni grafikoni
  06_network_metrics.py         centralnost + Louvain community detection
  07_visualize.py               glavna vizuelizacija mreže
  08_centrality_chart.py        panel grafikon top aktera po merama centralnosti
  09_build_report.py            sklapanje finalnog PDF izveštaja

data/raw/          sirovi JSON odgovori API-ja (po sezoni)
data/processed/    očišćeni CSV fajlovi (rezultati, mreža, metrike, zajednice)
figures/           generisani PNG grafikoni
report/izvestaj.pdf  finalni izveštaj
```

## Pokretanje (redosled)

Python 3.14, biblioteke: `pandas networkx matplotlib numpy requests python-louvain fpdf2`

```
python scripts/01_fetch_f1_data.py
python scripts/02_parse_f1_results.py
python scripts/03_manual_junior_career_data.py
python scripts/04_build_network.py
python scripts/05_eda.py
python scripts/06_network_metrics.py
python scripts/07_visualize.py
python scripts/08_centrality_chart.py
python scripts/09_build_report.py
```

Svaki skript čita ulaz iz `data/`, piše izlaz u `data/processed/` ili
`figures/` i može se ponovo pokrenuti nezavisno (rezultati prethodnih
koraka su već sačuvani na disku).

## Napomena o predaji

Pre predaje, u `report/izvestaj.pdf` (naslovna strana) treba upisati
ime, prezime i broj indeksa umesto placeholder teksta `[Ime Prezime,
broj indeksa]`, i predlog teme (ako još nije poslat) proslediti na
havzisara@gmail.com sa subjektom `ADM projekat – BrojIndeksa`.
