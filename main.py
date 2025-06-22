from tkinter import *
from tkinter import messagebox
import tkintermapview
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# === DANE PARKÓW ===
park_coords = {
    "Babiogórski_Park_Narodowy": (49.5969, 19.5242),
    "Białowieski_Park_Narodowy": (52.7027, 23.8539),
    "Biebrzański_Park_Narodowy": (53.4884, 22.6389),
    "Bieszczadzki_Park_Narodowy": (49.1328, 22.7214),
    "Bory_Tucholskie_Park_Narodowy": (53.7800, 17.5292),
    "Drawieński_Park_Narodowy": (53.1440, 15.8010),
    "Gorczański_Park_Narodowy": (49.5633, 20.2769),
    "Kampinoski_Park_Narodowy": (52.2995, 20.6897),
    "Karkonoski_Park_Narodowy": (50.7722, 15.7275),
    "Magurski_Park_Narodowy": (49.5280, 21.4266),
    "Narwiański_Park_Narodowy": (53.1108, 22.9964),
    "Ojcowski_Park_Narodowy": (50.2290, 19.8266),
    "Pieniński_Park_Narodowy": (49.4153, 20.4306),
    "Poleski_Park_Narodowy": (51.3785, 23.1440),
    "Roztoczański_Park_Narodowy": (50.6040, 23.2198),
    "Słowiński_Park_Narodowy": (54.7037, 17.4076),
    "Świętokrzyski_Park_Narodowy": (50.8622, 20.8910),
    "Tatrzański_Park_Narodowy": (49.2956, 19.9500),
    "Ujście_Warty_Park_Narodowy": (52.5669, 14.6836),
    "Wielkopolski_Park_Narodowy": (52.2736, 16.8421),
    "Wigierski_Park_Narodowy": (54.0355, 23.0841),
    "Woliński_Park_Narodowy": (53.9133, 14.4450),
    "Turnicki_Park_Narodowy": (49.5989, 22.7583)
}

parki = []
park_pracownicy = {}  # nazwa_parku -> lista obiektów Pracownik

class ParkNarodowy:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.latitude, self.longitude = park_coords.get(self.nazwa, (52.23, 21.0))
        self.marker = map_widget.set_marker(self.latitude, self.longitude, text=self.nazwa.replace("_", " "))

class Pracownik:
    def __init__(self, imie_nazwisko, miasto, nazwa_parku):
        self.imie_nazwisko = imie_nazwisko
        self.miasto = miasto
        self.nazwa_parku = nazwa_parku
        self.latitude, self.longitude = self.get_coordinates()
        self.marker = None

    def get_coordinates(self):
        try:
            url = f"https://nominatim.openstreetmap.org/search.php?q={quote(self.miasto)}&format=jsonv2"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            data = resp.json()
            return float(data[0]["lat"]), float(data[0]["lon"])
        except:
            return 52.23, 21.0

# === FUNKCJE PARKÓW ===
def usun_park():
    idx = listbox_parki.curselection()
    if not idx:
        return
    i = idx[0]
    park = parki[i]
    for p in park_pracownicy.get(park.nazwa, []):
        if p.marker:
            p.marker.delete()
    if park.marker:
        park.marker.delete()
    parki.pop(i)
    park_pracownicy.pop(park.nazwa, None)
    pokaz_parki()

def edytuj_park():
    idx = listbox_parki.curselection()
    if not idx:
        return
    i = idx[0]
    entry_nazwa.delete(0, END)
    entry_nazwa.insert(0, parki[i].nazwa.replace("_", " "))
    button_dodaj.config(text="Zapisz", command=lambda: zapisz_edycje(i))

def zapisz_edycje(i):
    nowa_nazwa = entry_nazwa.get().strip().replace(" ", "_")
    if not nowa_nazwa:
        return
    stara_nazwa = parki[i].nazwa
    if parki[i].marker:
        parki[i].marker.delete()
    parki[i] = ParkNarodowy(nowa_nazwa)
    park_pracownicy[nowa_nazwa] = park_pracownicy.pop(stara_nazwa, [])
    pokaz_parki()
    entry_nazwa.delete(0, END)
    button_dodaj.config(text="Dodaj park", command=dodaj_park)
def dodaj_park():
    nazwa = entry_nazwa.get().strip().replace(" ", "_")
    if not nazwa:
        return
    park = ParkNarodowy(nazwa)
    parki.append(park)
    park_pracownicy[nazwa] = []
    pokaz_parki()
    entry_nazwa.delete(0, END)
    entry_nazwa.focus()

def pokaz_parki():
    listbox_parki.delete(0, END)
    for i, park in enumerate(parki):
        listbox_parki.insert(i, f"{i+1}. {park.nazwa.replace('_', ' ')}")

def pokaz_na_mapie():
    idx = listbox_parki.curselection()
    if not idx:
        return
    park = parki[idx[0]]
    map_widget.set_position(park.latitude, park.longitude)
    map_widget.set_zoom(13)

def otworz_panel_pracownikow():
    idx = listbox_parki.curselection()
    if not idx:
        return
    park = parki[idx[0]]
    nazwa_parku = park.nazwa

    okno = Toplevel(root)
    okno.title(f"Pracownicy – {nazwa_parku.replace('_', ' ')}")
    okno.geometry("400x550")

    listbox = Listbox(okno, width=50, height=15)
    listbox.pack()

    def odswiez():
        listbox.delete(0, END)
        for i, p in enumerate(park_pracownicy[nazwa_parku]):
            listbox.insert(i, f"{i+1}. {p.imie_nazwisko} – {p.miasto}")

    def dodaj():
        imie = entry_imie.get().strip()
        miasto = entry_miasto.get().strip()
        if not imie or not miasto:
            return
        p = Pracownik(imie, miasto, nazwa_parku)
        park_pracownicy[nazwa_parku].append(p)
        odswiez()
        entry_imie.delete(0, END)
        entry_miasto.delete(0, END)

    def usun():
        sel = listbox.curselection()
        if not sel:
            return
        i = sel[0]
        if park_pracownicy[nazwa_parku][i].marker:
            park_pracownicy[nazwa_parku][i].marker.delete()
        park_pracownicy[nazwa_parku].pop(i)
        odswiez()

    def edytuj():
        sel = listbox.curselection()
        if not sel:
            return
        i = sel[0]
        p = park_pracownicy[nazwa_parku][i]
        entry_imie.delete(0, END)
        entry_imie.insert(0, p.imie_nazwisko)
        entry_miasto.delete(0, END)
        entry_miasto.insert(0, p.miasto)
        button_dodaj.config(text="Zapisz", command=lambda: zapisz(i))

    def zapisz(i):
        imie = entry_imie.get().strip()
        miasto = entry_miasto.get().strip()
        if not imie or not miasto:
            return
        if park_pracownicy[nazwa_parku][i].marker:
            park_pracownicy[nazwa_parku][i].marker.delete()
        park_pracownicy[nazwa_parku][i] = Pracownik(imie, miasto, nazwa_parku)
        odswiez()
        entry_imie.delete(0, END)
        entry_miasto.delete(0, END)
        button_dodaj.config(text="Dodaj pracownika", command=dodaj)

    def pokaz_na_mapie_wszystkich():
        pracownicy = park_pracownicy[nazwa_parku]
        if not pracownicy:
            return
        for p in pracownicy:
            if p.marker:
                p.marker.delete()
            p.marker = map_widget.set_marker(p.latitude, p.longitude, text=f"{p.imie_nazwisko}\n({p.miasto})")
        lat = sum(p.latitude for p in pracownicy) / len(pracownicy)
        lon = sum(p.longitude for p in pracownicy) / len(pracownicy)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(8)

    entry_imie = Entry(okno, width=40)
    entry_imie.pack()
    entry_imie.insert(0, "Imię i nazwisko")

    entry_miasto = Entry(okno, width=40)
    entry_miasto.pack()
    entry_miasto.insert(0, "Miasto")

    button_dodaj = Button(okno, text="Dodaj pracownika", command=dodaj)
    button_dodaj.pack(pady=2)

    Button(okno, text="Usuń pracownika", command=usun).pack(pady=2)
    Button(okno, text="Edytuj pracownika", command=edytuj).pack(pady=2)
    Button(okno, text="Pokaż wszystkich na mapie", command=pokaz_na_mapie_wszystkich).pack(pady=4)

    odswiez()

# === GUI ===
root = Tk()
root.title("Parki Narodowe – Mapa i Pracownicy")
root.geometry("1200x700")

ramka_lista = Frame(root)
ramka_formularz = Frame(root)
ramka_mapa = Frame(root)

ramka_lista.pack(side=LEFT, padx=10, pady=10)
ramka_formularz.pack(side=TOP, padx=10, pady=10)
ramka_mapa.pack(side=BOTTOM, padx=10, pady=10, fill=BOTH, expand=True)

Label(ramka_lista, text="Lista parków narodowych").pack()
listbox_parki = Listbox(ramka_lista, width=40, height=20)
listbox_parki.pack()
Button(ramka_lista, text="Pokaż na mapie", command=pokaz_na_mapie).pack(pady=2)
Button(ramka_lista, text="Usuń park", command=lambda: usun_park()).pack(pady=2)
Button(ramka_lista, text="Edytuj park", command=lambda: edytuj_park()).pack(pady=2)
Button(ramka_lista, text="Pracownicy", command=otworz_panel_pracownikow).pack(pady=5)

Label(ramka_formularz, text="Dodaj park (nazwa z Wikipedii):").pack()
entry_nazwa = Entry(ramka_formularz, width=40)
entry_nazwa.pack()
button_dodaj = Button(ramka_formularz, text="Dodaj park", command=dodaj_park)
button_dodaj.pack(pady=5)

map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=800, height=500, corner_radius=0)
map_widget.pack(fill=BOTH, expand=True)
map_widget.set_position(52.23, 21.0)
map_widget.set_zoom(6)

root.mainloop()
