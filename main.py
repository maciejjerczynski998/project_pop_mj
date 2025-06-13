from tkinter import *
from tkinter import messagebox
import tkintermapview
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# === RĘCZNY SŁOWNIK SIEDZIB PARKÓW NARODOWYCH ===
park_coords = {
    "Babiogórski_Park_Narodowy":     (49.5969, 19.5242),
    "Białowieski_Park_Narodowy":     (52.7027, 23.8539),
    "Biebrzański_Park_Narodowy":     (53.4884, 22.6389),
    "Bieszczadzki_Park_Narodowy":    (49.1328, 22.7214),
    "Bory_Tucholskie_Park_Narodowy": (53.7800, 17.5292),
    "Drawieński_Park_Narodowy":      (53.1440, 15.8010),
    "Gorczański_Park_Narodowy":      (49.5633, 20.2769),
    "Kampinoski_Park_Narodowy":      (52.2995, 20.6897),
    "Karkonoski_Park_Narodowy":      (50.7722, 15.7275),
    "Magurski_Park_Narodowy":        (49.5280, 21.4266),
    "Narwiański_Park_Narodowy":      (53.1108, 22.9964),
    "Ojcowski_Park_Narodowy":        (50.2290, 19.8266),
    "Pieniński_Park_Narodowy":       (49.4153, 20.4306),
    "Poleski_Park_Narodowy":         (51.3785, 23.1440),
    "Roztoczański_Park_Narodowy":    (50.6040, 23.2198),
    "Słowiński_Park_Narodowy":       (54.7037, 17.4076),
    "Świętokrzyski_Park_Narodowy":   (50.8622, 20.8910),
    "Tatrzański_Park_Narodowy":      (49.2956, 19.9500),
    "Ujście_Warty_Park_Narodowy":    (52.5669, 14.6836),
    "Wielkopolski_Park_Narodowy":    (52.2736, 16.8421),
    "Wigierski_Park_Narodowy":       (54.0355, 23.0841),
    "Woliński_Park_Narodowy":        (53.9133, 14.4450),
    "Turnicki_Park_Narodowy":        (49.5989, 22.7583),  # Planowany
}

parki = []

class ParkNarodowy:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.latitude, self.longitude = self.get_coordinates()
        self.marker = map_widget.set_marker(
            self.latitude, self.longitude, text=self.nazwa.replace("_", " ")
        )

    def get_coordinates(self):
        # 1️⃣ Sprawdź słownik lokalizacji siedzib
        coords = park_coords.get(self.nazwa)
        if coords:
            return coords

        # 2️⃣ Fallback – próbuj pobrać współrzędne z geo-dec Wikipedii
        try:
            url = f"https://pl.wikipedia.org/wiki/{quote(self.nazwa)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")

            geo = soup.select_one("span.geo-dec")
            if not geo:
                raise Exception("Nie znaleziono współrzędnych (geo-dec) na stronie Wikipedii.")

            parts = geo.text.strip().split()
            if len(parts) != 2:
                raise Exception("Nieprawidłowy format geo-dec.")

            lat = float(parts[0].replace("°N", "").replace("°S", "-"))
            lon = float(parts[1].replace("°E", "").replace("°W", "-"))

            return lat, lon

        except Exception as e:
            messagebox.showerror(
                "Błąd",
                f"Nie udało się pobrać współrzędnych dla „{self.nazwa.replace('_', ' ')}”.\nSzczegóły: {e}"
            )
            return 52.23, 21.0  # Warszawa – domyślna lokalizacja

def dodaj_park():
    nazwa = entry_nazwa.get().strip().replace(" ", "_")
    if not nazwa:
        messagebox.showwarning("Uwaga", "Wpisz nazwę parku.")
        return
    park = ParkNarodowy(nazwa)
    parki.append(park)
    pokaz_parki()
    entry_nazwa.delete(0, END)
    entry_nazwa.focus()

def pokaz_parki():
    listbox_parki.delete(0, END)
    for i, park in enumerate(parki):
        listbox_parki.insert(i, f"{i + 1}. {park.nazwa.replace('_', ' ')}")

def usun_park():
    idx = listbox_parki.curselection()
    if not idx:
        return
    i = idx[0]
    parki[i].marker.delete()
    parki.pop(i)
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
    parki[i].marker.delete()
    parki[i] = ParkNarodowy(nowa_nazwa)
    pokaz_parki()
    entry_nazwa.delete(0, END)
    button_dodaj.config(text="Dodaj park", command=dodaj_park)

def pokaz_na_mapie():
    idx = listbox_parki.curselection()
    if not idx:
        return
    park = parki[idx[0]]
    map_widget.set_position(park.latitude, park.longitude)
    map_widget.set_zoom(13)

# === GUI ===
root = Tk()
root.title("Parki Narodowe – Mapa")
root.geometry("1000x700")

# Ramki
ramka_lista = Frame(root)
ramka_formularz = Frame(root)
ramka_mapa = Frame(root)

ramka_lista.pack(side=LEFT, padx=10, pady=10)
ramka_formularz.pack(side=TOP, padx=10, pady=10)
ramka_mapa.pack(side=BOTTOM, padx=10, pady=10, fill=BOTH, expand=True)

# Lista parków
Label(ramka_lista, text="Lista parków narodowych").pack()
listbox_parki = Listbox(ramka_lista, width=40, height=20)
listbox_parki.pack()
Button(ramka_lista, text="Pokaż na mapie", command=pokaz_na_mapie).pack(pady=2)
Button(ramka_lista, text="Usuń park", command=usun_park).pack(pady=2)
Button(ramka_lista, text="Edytuj park", command=edytuj_park).pack(pady=2)

# Formularz
Label(ramka_formularz, text="Dodaj / edytuj park (nazwa z Wikipedii):").pack()
entry_nazwa = Entry(ramka_formularz, width=40)
entry_nazwa.pack()
button_dodaj = Button(ramka_formularz, text="Dodaj park", command=dodaj_park)
button_dodaj.pack(pady=5)

# Mapa
map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=800, height=500, corner_radius=0)
map_widget.pack(fill=BOTH, expand=True)
map_widget.set_position(52.23, 21.0)
map_widget.set_zoom(6)

root.mainloop()