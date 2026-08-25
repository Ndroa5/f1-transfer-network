"""Sklapa finalni PDF izveštaj (report/izvestaj.pdf)."""
import pathlib
import pandas as pd
from fpdf import FPDF

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIG_DIR = BASE_DIR / "figures"
REPORT_DIR = BASE_DIR / "report"
REPORT_DIR.mkdir(exist_ok=True)

FONT_DIR = pathlib.Path("C:/Windows/Fonts")

PAGE_W = 210
MARGIN = 18
CONTENT_W = PAGE_W - 2 * MARGIN


class Report(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Arial", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 8, "Analiza mreže transfera vozača Formule 1", align="L")
        self.cell(0, 8, f"{self.page_no()}", align="R")
        self.ln(12)

    def footer(self):
        pass


def add_fonts(pdf: Report):
    pdf.add_font("Arial", "", str(FONT_DIR / "arial.ttf"))
    pdf.add_font("Arial", "B", str(FONT_DIR / "arialbd.ttf"))
    pdf.add_font("Arial", "I", str(FONT_DIR / "ariali.ttf"))
    pdf.add_font("Arial", "BI", str(FONT_DIR / "arialbi.ttf"))


def h1(pdf, text):
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(20, 20, 20)
    pdf.ln(2)
    pdf.set_x(MARGIN)
    pdf.multi_cell(CONTENT_W, 9, text)
    pdf.set_draw_color(180, 60, 60)
    pdf.set_line_width(0.6)
    y = pdf.get_y() + 1
    pdf.line(MARGIN, y, MARGIN + CONTENT_W, y)
    pdf.ln(5)


def h2(pdf, text):
    pdf.set_font("Arial", "B", 12.5)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(3)
    pdf.set_x(MARGIN)
    pdf.multi_cell(CONTENT_W, 7, text)
    pdf.ln(1)


def p(pdf, text, size=10.3, gap=3):
    pdf.set_font("Arial", "", size)
    pdf.set_text_color(35, 35, 35)
    pdf.set_x(MARGIN)
    pdf.multi_cell(CONTENT_W, 5.6, text)
    pdf.ln(gap)


def bullet(pdf, text, size=10.3):
    pdf.set_font("Arial", "", size)
    pdf.set_text_color(35, 35, 35)
    pdf.set_x(MARGIN + 4)
    pdf.multi_cell(CONTENT_W - 4, 5.6, f"\u2022  {text}")


def caption(pdf, text):
    pdf.set_font("Arial", "I", 8.7)
    pdf.set_text_color(110, 110, 110)
    pdf.set_x(MARGIN)
    pdf.multi_cell(CONTENT_W, 4.6, text, align="C")
    pdf.ln(3)


def image_full(pdf, path, caption_text):
    pdf.image(str(path), x=MARGIN, w=CONTENT_W)
    caption(pdf, caption_text)


def table(pdf, headers, rows, col_widths, size=8.6, header_fill=(230, 230, 235)):
    pdf.set_x(MARGIN)
    pdf.set_font("Arial", "B", size)
    pdf.set_fill_color(*header_fill)
    for htext, w in zip(headers, col_widths):
        pdf.cell(w, 6.5, htext, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", size)
    for row in rows:
        pdf.set_x(MARGIN)
        for val, w in zip(row, col_widths):
            pdf.cell(w, 6, str(val), border=1)
        pdf.ln()
    pdf.ln(3)


def main():
    metrics = pd.read_csv(PROCESSED_DIR / "network_metrics.csv")
    edges = pd.read_csv(PROCESSED_DIR / "network_edges.csv")
    comms = pd.read_csv(PROCESSED_DIR / "network_communities.csv")
    nodes = pd.read_csv(PROCESSED_DIR / "network_nodes.csv")
    junior = pd.read_csv(PROCESSED_DIR / "junior_career_manual.csv")
    results = pd.read_csv(PROCESSED_DIR / "f1_race_results_2018_2025.csv")

    pdf = Report(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    add_fonts(pdf)
    pdf.set_margins(MARGIN, 16, MARGIN)

    # ---------------- naslovna strana ----------------
    def center_line(txt, h):
        pdf.set_x(MARGIN)
        pdf.multi_cell(CONTENT_W, h, txt, align="C")

    pdf.add_page()
    pdf.ln(55)
    pdf.set_font("Arial", "B", 22)
    pdf.set_text_color(15, 15, 15)
    center_line("Analiza mreže transfera vozača Formule 1", 11)
    pdf.ln(2)
    pdf.set_font("Arial", "", 14)
    pdf.set_text_color(90, 90, 90)
    center_line("Identifikacija akademija, feeder timova i ključnih aktera", 8)
    pdf.ln(14)
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(60, 60, 60)
    center_line("Projekat iz predmeta Analiza društvenih mreža", 6.5)
    center_line("[Ime Prezime, broj indeksa]", 6.5)
    center_line("24. avgust 2026.", 6.5)
    pdf.ln(20)
    pdf.set_font("Arial", "I", 9.5)
    pdf.set_text_color(130, 130, 130)
    center_line(
        "Napomena: pre početka rada na projektu, predlog teme je potrebno poslati na havzisara@gmail.com "
        "sa obaveznim subjektom \"ADM projekat – BrojIndeksa\" (ili \"ADM projekat – BrojIndeksa, BrojIndeksa\" za rad u paru).",
        5.5)

    # ---------------- 1. Uvod ----------------
    pdf.add_page()
    h1(pdf, "1. Uvod i opis teme")
    p(pdf,
      "Formula 1 je sport u kome vozači retko dolaze direktno „sa ulice” – gotovo svaki vozač na gridu prošao "
      "je kroz višegodišnji, institucionalizovan sistem razvoja: karting, junior formule (F4, F3, Formula 2/GP2), "
      "često uz podršku zvaničnog programa mladih vozača („akademije”) koji vodi jedan od F1 konstruktora. Ovaj "
      "sistem čini svojevrsnu mrežu talenta: akademije investiraju u vozače, vozači se takmiče za timove u nižim "
      "kategorijama („feeder timovi”), a na kraju (eventualno) dobijaju sedišta u F1 timovima – često ne kod "
      "konstruktora koji ih je razvio, već kod konkurencije.")
    p(pdf,
      "Cilj ovog projekta je da se ta mreža eksplicitno rekonstruiše iz podataka o stvarnim karijerama vozača i "
      "analizira kao usmerena, ponderisana mreža karijernih prelaza. Konkretno, projekat pokušava da odgovori na "
      "sledeća pitanja:")
    bullet(pdf, "Koje akademije konstruktora su najproduktivnije – tj. najčešće „proizvode” vozače koji stignu do F1?")
    bullet(pdf, "Koji junior/feeder timovi (F2, GP2, F3...) su najznačajniji čvorovi u lancu snabdevanja talentom, i da li opslužuju više akademija istovremeno?")
    bullet(pdf, "Koji entiteti (timovi ili akademije) deluju kao strukturni „mostovi” između različitih delova mreže?")
    bullet(pdf, "Postoje li slučajevi „curenja” talenta – vozač koga je razvila jedna akademija, a koji na kraju vozi za direktnog konkurenta?")
    bullet(pdf, "Da li se mreža prirodno razlaže na prepoznatljive „ekosisteme” (zajednice) oko pojedinih konstruktora?")
    pdf.ln(2)
    p(pdf,
      "Obuhvat podataka je namerno ograničen na sezone 2018-2025 (tzv. moderna era). Formalni programi mladih "
      "vozača (Red Bull Junior Team, Ferrari Driver Academy, Mercedes Junior Team, Alpine/Renault Sport Academy, "
      "McLaren Driver Development Programme, Williams Driver Academy, Sauber Academy) su moderan fenomen – većina "
      "je uspostavljena između 2001. i 2019. godine. Proširivanje obuhvata na celu istoriju F1 (od 1950.) bi mrežu "
      "„razvodnilo” decenijama u kojima akademije formalno nisu ni postojale, što bi oslabilo baš onaj deo teme "
      "koji je u fokusu specifikacije projekta (identifikacija akademija i feeder timova). Ova odluka o obimu je "
      "svesna metodološka odluka, ne ograničenje dostupnih podataka.")

    # ---------------- 2. Podaci ----------------
    pdf.add_page()
    h1(pdf, "2. Opis podataka i načina prikupljanja")
    h2(pdf, "2.1 Izvor A: rezultati trka Formule 1 (API)")
    p(pdf,
      "Osnovni, objektivno proverljiv sloj podataka je istorija nastupa vozača po konstruktorima, prikupljena "
      f"kroz {results.shape[0]} redova (kombinacija vozač x trka, {results.groupby(['season','round']).ngroups} trka, "
      "sezone 2018-2025) sa Jolpica-F1 API-ja (https://api.jolpi.ca/ergast), besplatnog, javnog REST API-ja koji "
      "predstavlja nastavak ugašenog Ergast Developer API-ja i koristi identičnu šemu podataka. Podaci su preuzeti "
      "24.8.2026. metodom HTTP GET, bez autentifikacije, iz rezultata trka po sezoni "
      "(scripts/01_fetch_f1_data.py), a zatim parsirani u jedinstvenu tabelu (scripts/02_parse_f1_results.py).")
    p(pdf,
      "Ograničenje: API je community-održavan nastavak Ergast-a, pa su moguća povremena kašnjenja/odstupanja za "
      "vrlo skorašnje trke u odnosu na zvanične FIA podatke. Sirovi podaci su sačuvani odvojeno od obrađenih "
      "(data/raw/ vs data/processed/), u skladu sa zahtevom specifikacije projekta.")

    h2(pdf, "2.2 Izvor B: pripadnost akademiji i junior/feeder timu (ručno kurirano)")
    p(pdf,
      "Ne postoji besplatan, mašinski čitljiv API koji povezuje F1 vozače sa njihovim junior-kategorija timovima i "
      "akademijama – Ergast/Jolpica pokriva isključivo F1 nivo. Ovaj sloj podataka je zato ručno kuriran "
      "(scripts/03_manual_junior_career_data.py), što je eksplicitno dozvoljeno specifikacijom projekta uz uslov "
      "jasnog obrazloženja. Metod: za svakog od 43 vozača u F1 skupu (2018-2025) beležena je (približna) godina "
      "ulaska u akademiju konstruktora i/ili junior tim, na osnovu javno dostupnih izvora – prevashodno Wikipedia "
      "stranica pojedinačnih akademija i sezona FIA Formula 2/GP2 prvenstva, dohvaćenih 24.8.2026, unakrsno "
      "provereno sa opštim javnim znanjem o karijerama vozača.")
    n_drivers = results["driver_id"].nunique()
    n_with_junior = junior["driver_id"].nunique()
    p(pdf,
      f"Pokrivenost: {n_with_junior}/{n_drivers} vozača ({100*n_with_junior/n_drivers:.0f}%) ima bar jedan zapis. "
      "Preostala tri vozača (Kimi Raikkonen, Fernando Alonso, Valtteri Bottas) NEMAJU zapis – i to je namerni "
      "nalaz, ne propust: Raikkonen i Alonso su prešli u F1 bez prolaska kroz GP2/F2 korak (poznati „skip” "
      "slučajevi), a Bottas je bio neformalni test-vozač Williamsa pre nego što je „Williams Driver Academy” "
      "kao formalni entitet uopšte osnovan (2019).")
    p(pdf,
      "Svaki zapis nosi oznaku pouzdanosti: VISOKA za vozače čija je F2/GP2 postava unakrsno proverena sa "
      "Wikipedia tabelama postave timova po sezoni (najviše pouzdanja za eru 2017+), SREDNJA/NISKA za starije "
      "vozače (GP2/GP3/F3 era pre 2017) gde se oslanjamo na opšte poznate činjenice bez sistematske provere "
      "svakog detalja. Model svesno pojednostavljuje: svaki vozač ima najviše JEDNU „primarnu” akademiju, iako "
      "je stvarna pripadnost ponekad bila neformalna ili promenljiva (npr. Alexander Albon je rano bio u Red Bull "
      "programu, ispao iz njega, pa se vratio u Red Bull-ov F1 tim godinama kasnije bez formalne akademije u "
      "međuvremenu – mreža ovo tačno reflektuje kao dva odvojena koraka).")

    h2(pdf, "2.3 Metodološka napomena: kanonizacija rebrendiranih timova")
    p(pdf,
      "Više F1 konstruktora je u posmatranom periodu promenilo sponzorsko ime uz zadržavanje iste fabrike/osoblja "
      "(npr. Toro Rosso -> AlphaTauri -> RB; Force India -> Racing Point -> Aston Martin; Renault -> Alpine; "
      "Sauber -> Alfa Romeo -> Sauber). Pošto nas zanima stvarni tok talenta kroz ORGANIZACIJE a ne kroz nazive "
      "pojedinačnih sezona, ovi lanci su svedeni na po jedan kanonski čvor. Isto je urađeno za nekoliko F2/GP2 "
      "timova koji su promenili naziv sponzora (npr. Hitech Grand Prix / Hitech Pulse-Eight; Russian Time / "
      "UNI-Virtuosi / Virtuosi / Invicta Virtuosi / Invicta Racing). Ovo je svesna metodološka odluka koja "
      "direktno utiče na strukturu mreže – bez nje bi se npr. veza „Red Bull-ov junior tim -> Red Bull Racing” "
      "veštački razbila na tri različita, slabija para grana.")

    # ---------------- 3. EDA ----------------
    pdf.add_page()
    h1(pdf, "3. Eksplorativna analiza sirovih podataka")
    p(pdf,
      "Pre gradnje mreže, sirovi podaci su pregledani radi otkrivanja problema. Otkrivena su i rešena dva "
      "konkretna problema:")
    bullet(pdf,
        "Paginacija API-ja je zasnovana na broju REZULTATA, ne broju trka – zbog toga se ista trka (npr. Miami "
        "Grand Prix 2024) u sirovom JSON-u ponekad pojavljuje dvaput, svaki put sa različitim podskupom vozača. "
        "Rešeno spajanjem zapisa po (sezona, krug) pre bilo kakve analize (scripts/02_parse_f1_results.py).")
    bullet(pdf,
        "Pri prvoj verziji gradnje mreže, vozač koji se u istoj sezoni vratio istom timu posle kratkog nastupa "
        "za drugi tim (npr. George Russell koji je 2020. jednom zamenio Hamiltona kod Mercedesa pa se vratio "
        "Williamsu) bio je greškom DUPLO brojan na istoj grani. Rešeno pravilom da se isti vozač računa najviše "
        "jednom po grani – težina grane je broj RAZLIČITIH vozača, ne broj događaja.")
    p(pdf,
      f"Obrađeni skup obuhvata {n_drivers} jedinstvenih vozača, {results['constructor_id'].nunique()} "
      f"originalnih (pre kanonizacije) konstruktorskih identiteta, kroz {results.groupby(['season','round']).ngroups} "
      "trka u 8 sezona. Nema nedostajućih vrednosti (missing values) ni u jednoj koloni obrađene tabele rezultata.")
    image_full(pdf, FIG_DIR / "eda_races_per_season.png",
               "Slika 1. Broj trka po sezoni – vidljiv je rast kalendara (2020. skraćen zbog COVID-19 pandemije; 2024-2025 najduži kalendari u istoriji F1).")
    image_full(pdf, FIG_DIR / "eda_races_per_driver.png",
               "Slika 2. Broj odvoženih trka po vozaču u periodu 2018-2025 – razlikuje stalne vozače od rezervi/zamena sa svega par nastupa.")
    image_full(pdf, FIG_DIR / "eda_teams_per_driver.png",
               "Slika 3. Broj različitih (originalnih, pre kanonizacije) F1 konstruktora po vozaču – preliminarni indikator „transfer aktivnosti” pre finalne mrežne analize.")

    # ---------------- 4. Mreza ----------------
    pdf.add_page()
    h1(pdf, "4. Konstrukcija i tip mreže")
    p(pdf,
      "Mreža je izgrađena kao USMERENA, PONDERISANA mreža karijernih prelaza (scripts/04_build_network.py). "
      "Čvorovi predstavljaju tri tipa entiteta:")
    bullet(pdf, "akademija konstruktora (npr. Red Bull Junior Team, Ferrari Driver Academy) – 7 čvorova;")
    bullet(pdf, "junior/feeder tim u nižoj seriji (F2, GP2, GP3, F3...) – 18 čvorova;")
    bullet(pdf, "F1 tim (kanonizovan kroz rebrendiranja) – 10 čvorova.")
    pdf.ln(1)
    p(pdf,
      "Grana A -> B postoji ako je bar jedan vozač napravio TAČNO taj prelaz kao dva UZASTOPNA koraka svoje "
      "karijere (npr. „Ferrari Driver Academy -> Prema Racing” ili „RB -> Red Bull Racing”). Težina grane je "
      "broj različitih vozača koji su napravili taj prelaz – viša težina znači češći, „utabaniji” put. Mreža je "
      "usmerena jer smer prelaska nosi značenje (napredovanje kroz akademiju je fundamentalno drugačiji događaj "
      "od povratka u nižu kategoriju), a ponderisana jer nam je bitno KOLIKO vozača deli isti put, ne samo da li "
      "put postoji.")
    n_nodes, n_edges = len(nodes), len(edges)
    p(pdf,
      f"Rezultujuća mreža ima {n_nodes} čvorova i {n_edges} usmerenih grana, gustinu (density) 0.098 i čini JEDNU "
      "slabo povezanu komponentu (weakly connected) – odnosno, ne postoje potpuno izolovani „ostrvski” delovi "
      "mreže, što je očekivano s obzirom da svi vozači na kraju prolaze kroz F1 sloj.")

    h2(pdf, "4.1 Koje mere centralnosti su korisne za ovu mrežu")
    p(pdf,
      "Zbog usmerenosti i tro-slojne (akademija -> feeder tim -> F1 tim) prirode mreže, koristimo četiri "
      "komplementarne mere:")
    bullet(pdf, "TEŽINSKI ULAZNI STEPEN (in-degree) – koji entiteti PRIMAJU najviše (različitih) vozača; u kontekstu teme identifikuje F1 timove koji funkcionišu kao „ulazna vrata” za rookije.")
    bullet(pdf, "TEŽINSKI IZLAZNI STEPEN (out-degree) – koji entiteti „PROIZVODE” najviše vozača dalje niz mrežu; direktno meri produktivnost akademije/feeder tima.")
    bullet(pdf, "BETWEENNESS (POSREDNIČKA) CENTRALNOST – koji čvorovi leže na najviše najkraćih puteva između ostalih parova čvorova; identifikuje STRUKTURNE MOSTOVE koji povezuju različite delove mreže (npr. različite „ekosisteme” akademija).")
    bullet(pdf, "PAGERANK (težinski) – rekurzivna mera „ugleda” koja uzima u obzir i važnost čvorova koji vode ka datom čvoru; u ovoj mreži favorizuje F1 timove koji primaju vozače iz već uticajnih feedera.")

    # ---------------- 5. Rezultati ----------------
    pdf.add_page()
    h1(pdf, "5. Rezultati: mere centralnosti i ključni akteri")
    p(pdf, "Kompletna mreža (Slika 4) je zbog broja čvorova prikazana na posebnoj stranici u položenom formatu radi čitljivosti oznaka.")

    # posebna landscape stranica za veliku mrežnu vizuelizaciju
    pdf.add_page(orientation="L")
    lw = 297 - 2 * MARGIN
    img_y = 28
    pdf.image(str(FIG_DIR / "network_full.png"), x=MARGIN, y=img_y, w=lw)
    pdf.set_y(img_y + lw * (2210 / 4420) + 4)
    pdf.set_x(MARGIN)
    pdf.set_font("Arial", "I", 8.7)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(lw, 4.6,
        "Slika 4. Kompletna mreža karijernih prelaza (2018-2025). Boja = detektovana Louvain zajednica; "
        "veličina čvora = težinski PageRank; debljina grane = broj vozača koji su napravili taj prelaz.",
        align="C")

    pdf.add_page()
    image_full(pdf, FIG_DIR / "centrality_panel.png",
               "Slika 5. Top 8 čvorova po četiri mere centralnosti, obojeno po tipu čvora.")

    h2(pdf, "5.1 Najjače pojedinačne grane („utabani putevi”)")

    def short(name, n=24):
        return name if len(name) <= n else name[: n - 1] + "…"

    top_edges = edges.sort_values("weight", ascending=False).head(10)
    table(pdf, ["Od", "Do", "Tež.", "Vozači"],
          [[short(r.source), short(r.target), r.weight, (r.drivers[:44] + "...") if len(r.drivers) > 44 else r.drivers]
           for r in top_edges.itertuples()],
          [42, 42, 10, 80])

    h2(pdf, "5.2 Detekcija zajednica (Louvain)")
    n_comms = comms["community"].nunique()
    p(pdf,
      "Primenom Louvain algoritma na neusmerenu, težinsku projekciju mreže (grane A<->B spojene sabiranjem "
      f"težina) dobijene su {n_comms} zajednice sa modularnošću 0.329 – umerena, jasno prepoznatljiva struktura "
      "(vrednosti iznad ~0.3 se uobičajeno smatraju značajnom podelom na zajednice). Sadržaj zajednica se dobro "
      "poklapa sa poznatom stvarnošću F1 sveta:")
    for c in sorted(comms["community"].unique()):
        members = comms[comms["community"] == c].merge(nodes, on=["node_id", "node_type"])
        names = ", ".join(members["node_id"].tolist())
        bullet(pdf, f"Zajednica {c} ({len(members)} članova): {names}")

    # ---------------- 6. Interpretacija ----------------
    pdf.add_page()
    h1(pdf, "6. Interpretacija: akademije, feeder timovi i ključni akteri")

    h2(pdf, "6.1 Prema Racing – dominantan, „multi-brendovski” feeder tim")
    p(pdf,
      "Prema Racing ima najveći težinski izlazni stepen među junior timovima (9) i najveći ulazni stepen među "
      "svim junior/feeder timovima (9, izjednačeno sa Sauberom kao najvišim rezultatom među F1 timovima) – kroz "
      "njega su prošli vozači iz ČETIRI različite akademije (Ferrari, Mercedes, Alpine, McLaren), što je jasno "
      "vidljivo i u community detekciji: Prema Racing je svrstan u istu, „multi-akademijsku” Zajednicu 3 zajedno "
      "sa Ferrari/Mercedes/Alpine/McLaren akademijama, Mercedesovim i Sauberovim F1 timom. Najjača pojedinačna "
      "grana u celoj mreži je baš „Ferrari Driver Academy -> Prema Racing” (5 vozača: Bearman, Giovinazzi, "
      "Leclerc, Schumacher, Stroll). Ovo potvrđuje široko poznatu činjenicu iz sveta motosporta – Prema Racing "
      "(italijanski tim iz Ferrari Driver Academy okruženja) je de facto „neutralna” elitna škola za mlade "
      "vozače, bez obzira čiji su formalno stipendisti.")

    h2(pdf, "6.2 Red Bull Junior Team – najagresivnija akademija")
    p(pdf,
      "Red Bull Junior Team ima ubedljivo najveći težinski izlazni stepen (11) među svim čvorovima mreže – više "
      "nego duplo u odnosu na drugu najproduktivniju akademiju (Ferrari Driver Academy, 7). U kombinaciji sa "
      "granom „RB (Toro Rosso/AlphaTauri) -> Red Bull Racing” (4 vozača: Albon, Gasly, Lawson, Tsunoda) i "
      "obrnutom granom „Red Bull Racing -> RB” (2 vozača: Gasly, Lawson, degradirani nazad), mreža jasno "
      "pokazuje Red Bullov prepoznatljiv, agresivan model: RB (bivši Toro Rosso/AlphaTauri) funkcioniše kao "
      "eksplicitno „sito” – mesto gde se mladi vozači iz akademije testiraju u realnim F1 uslovima pre "
      "(eventualnog) unapređenja u glavni tim, ili vraćaju ako ne zadovolje. Community detekcija ovo prepoznaje "
      "kao zasebnu, kompaktnu Zajednicu 2 (Red Bull Junior Team + RB + Red Bull Racing + njihovi karakteristični "
      "feeder timovi Carlin, DAMS, Hitech, MW Arden).")

    h2(pdf, "6.3 Williams – „ulazna vrata” u Formulu 1")
    p(pdf,
      "Williams ima najveći težinski ulazni stepen (12) I najveću betweenness centralnost (0.28) u celoj mreži – "
      "kombinacija koja ga izdvaja kao strukturno najznačajniji pojedinačni čvor. Ovo se poklapa sa poznatom "
      "reputacijom Williamsa u ovom periodu kao tima koji je (usled ograničenog budžeta) često davao F1 debije "
      "mladim/plaćenim vozačima (Latifi, Russell, Aitken, Sargeant, Colapinto) umesto etabliranih imena – što "
      "mreža nezavisno potvrđuje kroz strukturu podataka, a ne kroz eksternu reputaciju. Williams Driver Academy "
      "(osnovana 2019) takođe ima visoku betweenness centralnost (0.23, drugo mesto u mreži), što pokazuje da "
      "je taj deo mreže – iako mlađi od konkurentskih akademija – već strukturno značajan most.")

    h2(pdf, "6.4 „Curenje” talenta: kada akademija razvije vozača za konkurenta")
    p(pdf,
      "Mreža otkriva dva narativno važna slučaja u kojima vozač završi u F1 timu KOJI NIJE vezan za akademiju koja "
      "ga je razvila:")
    bullet(pdf,
        "Oscar Piastri je bio član Alpine Academy (2020-2022, F2 šampion 2021), ali je za sezonu 2023. potpisao za "
        "McLaren umesto Alpine F1 tima – poznat, javno vrlo komentarisan slučaj ugovornog spora. U mreži se ovo "
        "vidi kao grana „Alpine Academy -> Prema Racing -> McLaren”, bez ijedne grane ka Alpine (Renault) F1 timu.")
    bullet(pdf,
        "Gabriel Bortoleto je bio član McLaren Driver Development Programme (2023-2024, šampion F3 2023. kao "
        "McLarenov stipendista), ali je F1 debi 2025. napravio za Sauber – McLaren u tom trenutku nije imao slobodno "
        "sedište (Norris i Piastri su već bili ugovoreni). Mreža ovo pokazuje kao „McLaren Driver Development "
        "Programme -> Invicta Racing -> Sauber (Alfa Romeo)”.")
    p(pdf,
      "Oba slučaja ilustruju strukturno ograničenje akademskog modela: broj F1 sedišta po timu je fiksiran na dva, "
      "pa i uspešna akademija redovno „izgubi” svoje najbolje diplomce konkurenciji kada sopstvena sedišta nisu "
      "slobodna.")

    h2(pdf, "6.5 Sauber/Alfa Romeo – visok uticaj bez sopstvene akademije")
    p(pdf,
      "Sauber (Alfa Romeo) ima treći najveći težinski ulazni stepen (9) i drugi najveći PageRank u celoj mreži "
      "(0.131, odmah iza Ferrarija) – ali, zanimljivo, NIJEDAN vozač u ovom skupu nije stigao do Sauberovog F1 "
      "sedišta kroz SOPSTVENU (Sauber Academy) akademiju; umesto toga, Sauber prima diplomce Ferrari akademije "
      "(Giovinazzi, Leclerc pre prelaska u Ferrari, Zhou) i – kao u prethodnoj tački – McLarenove akademije "
      "(Bortoleto). Ovo je dobra ilustracija da visoka centralnost F1 tima ne mora poticati iz njegovog "
      "sopstvenog pipeline-a već iz pozicije „prijemnog” tima za tuđe diplomce – često zahvaljujući Ferrarijevom "
      "motoru i dugogodišnjim neformalnim vezama Sauber-Ferrari.")

    h2(pdf, "6.6 Vozači bez formalnog pipeline-a")
    p(pdf,
      "Kimi Raikkonen i Fernando Alonso su u ovom skupu jedini vozači koji u mreži nemaju nijednu ulaznu granu – "
      "obojica su u F1 ušli bez akademije i bez GP2/F2 koraka (Raikkonen je 2001. dobio Super License posle svega "
      "23 nastupa u nižim formulama, što je i danas jedan od najekstremnijih slučajeva u istoriji sporta; Alonso "
      "je prešao direktno iz Euro F3000-a 2001. godine). Njihovo odsustvo iz mreže NIJE nedostatak podataka već "
      "tačna reprezentacija stvarnosti: to su vozači čija karijera nikad nije prošla kroz današnji, "
      "institucionalizovani model razvoja talenta.")

    # ---------------- 7. Zakljucak ----------------
    pdf.add_page()
    h1(pdf, "7. Zaključci i uvidi")
    p(pdf,
      "Analiza mreže karijernih prelaza vozača Formule 1 (2018-2025) pokazuje da moderni F1 talent-sistem ima "
      "jasnu, merljivu strukturu koja se poklapa sa opšte poznatim narativima sporta, ali ih i precizira brojkama:")
    bullet(pdf, "Akademije se značajno razlikuju po „produktivnosti” – Red Bull Junior Team (izlazni stepen 11) je u ovom periodu ubedljivo najagresivnija i najproduktivnija, dok je Sauber Academy, uprkos godinama ulaganja, u ovom periodu proizvela nula direktnih F1 diplomaca iz našeg skupa.")
    bullet(pdf, "Nekoliko elitnih junior timova (pre svega Prema Racing) funkcioniše kao zajednička infrastruktura VIŠE konkurentskih akademija istovremeno – „feeder tim” i „akademija” nisu isti pojam, i mreža to jasno razdvaja.")
    bullet(pdf, "Williams se strukturno izdvaja kao glavna „ulazna vrata” u F1 (najveći in-degree i betweenness), što je nezavisna, podacima potkrepljena potvrda njegove reputacije tima koji najčešće daje F1 debije.")
    bullet(pdf, "Akademijski pipeline nije garancija sedišta kod „matičnog” tima – Piastri i Bortoleto su najizrazitiji primeri u ovom skupu, oba zbog ograničenog broja sedišta (dva po timu) u trenutku kada su bili spremni za F1.")
    bullet(pdf, "Community detekcija (4 zajednice, modularnost 0.329) nezavisno potvrđuje da mreža ima prepoznatljivu „ekosistemsku” strukturu organizovanu prevashodno oko pojedinačnih konstruktora (Red Bull, Williams), sa jednim širim, „mešovitim” ekosistemom oko Ferrari/Mercedes/Alpine/McLaren akademija i Prema Racinga.")

    h2(pdf, "Ograničenja")
    bullet(pdf, "Ručno kurirani sloj podataka (akademija/junior tim) je najpouzdaniji za vozače koji su vozili F2 u modernoj eri (2017+); za starije vozače (GP2/GP3/F3 pre 2017) pouzdanost je srednja do niska.")
    bullet(pdf, "Model dozvoljava najviše jednu „primarnu” akademiju po vozaču, što pojednostavljuje nekoliko realno neformalnijih/promenljivih slučajeva (npr. rani, prekinuti odnos Albona sa Red Bullom).")
    bullet(pdf, "Karting nivo i F4/F3 kategorije nisu sistematski uključeni – mreža počinje uglavnom od F2/GP2 nivoa naviše, što je svesno zadržano radi kvaliteta i provere podataka.")
    bullet(pdf, "Obuhvat je namerno ograničen na 2018-2025; širi istorijski obuhvat bi zahtevao znatno više ručnog istraživanja uz nižu pouzdanost.")

    h2(pdf, "Mogući pravci daljeg rada")
    bullet(pdf, "Proširiti mrežu na F3/F4/karting nivo radi potpunijeg pipeline-a od najranijih koraka karijere.")
    bullet(pdf, "Dodati vremensku dimenziju (dinamička mreža po sezonama) radi praćenja evolucije uticaja pojedinih akademija kroz vreme.")
    bullet(pdf, "Uključiti podatke o sponzorstvu/finansiranju („pay driver” dinamika) kao dodatni atribut grana, s obzirom da je to poznat konfundirajući faktor u F1 transferima (npr. slučaj Stroll/Williams-Aston Martin).")

    out_path = REPORT_DIR / "izvestaj.pdf"
    pdf.output(str(out_path))
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
