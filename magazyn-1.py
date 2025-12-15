import streamlit as st
import pandas as pd
from collections import Counter

# --- Inicjalizacja Stanu Sesji ---
# Sprawdzamy, czy 'towary' już istnieją w stanie sesji. 
# Jeśli nie, inicjalizujemy pustą listę.
if 'towary' not in st.session_state:
    st.session_state['towary'] = []

# --- Funkcje do Zarządzania Magazynem ---

def dodaj_towar(nazwa):
    """Dodaje towar do listy."""
    # Używamy st.form, więc ta funkcja jest wywoływana tylko po kliknięciu 'Dodaj'
    if nazwa and nazwa.strip():
        towar_czysty = nazwa.strip()
        st.session_state['towary'].append(towar_czysty)
        st.success(f"Dodano towar: **{towar_czysty}**")
        
    else:
        st.warning("Nazwa towaru nie może być pusta.")

def usun_towar(nazwa):
    """Usuwa pierwsze wystąpienie towaru z listy."""
    try:
        st.session_state['towary'].remove(nazwa)
        st.info(f"Usunięto towar: **{nazwa}**")
    except ValueError:
        st.error(f"Błąd: Nie znaleziono towaru o nazwie **{nazwa}** na liście.")

# --- Interfejs Użytkownika (Streamlit) ---

st.title("📦 Prosty Magazyn Towarów v2.0")
st.markdown("Aplikacja używa list w pamięci (sesyjny stan Streamlit). Dane **zostaną utracone** po odświeżeniu/zamknięciu.")

# 1. Sekcja Dodawania Towaru
st.header("➕ Dodaj Nowy Towar")
with st.form("form_dodawania", clear_on_submit=True): # Dodano 'clear_on_submit=True' dla upewnienia się
    # Zmieniono klucz na 'input_dodaj_v2' - na wszelki wypadek
    nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj_v2") 
    submitted_add = st.form_submit_button("Dodaj")
    
    if submitted_add:
        # Wywołanie funkcji z wartością z pola tekstowego
        dodaj_towar(nowy_towar) 
        # UWAGA: Usunięto błądzącą linię: st.session_state.input_dodaj = "" 
        # Formularz resetuje się automatycznie dzięki clear_on_submit=True

st.markdown("---")

# 2. Sekcja Usuwania Towaru
st.header("➖ Usuń Towar")

if st.session_state['towary']:
    # Używamy Counter do zliczenia, a następnie sortujemy unikalne nazwy dla przejrzystości
    liczniki = Counter(st.session_state['towary'])
    opcje_do_usuniecia = sorted([f"{nazwa} (Dostępnych: {ilosc})" for nazwa, ilosc in liczniki.items()])
    
    with st.form("form_usuwania"):
        towar_info_do_usuniecia = st.selectbox(
            "Wybierz towar do usunięcia (usuwa **jedno** wystąpienie):",
            opcje_do_usuniecia,
            key="input_usun"
        )
        submitted_remove = st.form_submit_button("Usuń Wybrany Towar")

        if submitted_remove and towar_info_do_usuniecia:
            # Wyczyść nazwy towaru z informacji o ilości
            towar_do_usuniecia = towar_info_do_usuniecia.split(" (Dostępnych:")[0].strip()
            usun_towar(towar_do_usuniecia)
else:
    st.info("Brak towarów do usunięcia.")

st.markdown("---")

# 3. Sekcja Wyświetlania Stanu Magazynu
st.header("📋 Aktualny Stan Magazynu")

if st.session_state['towary']:
    # Obliczanie liczby wystąpień każdego towaru
    liczniki_final = Counter(st.session_state['towary'])
    
    # Przygotowanie danych do wyświetlenia w DataFrame
    dane_do_tabeli = [
        {"Nazwa Towaru": nazwa, "Ilość": ilosc} 
        for nazwa, ilosc in sorted(liczniki_final.items())
    ]
    
    df = pd.DataFrame(dane_do_tabeli)
    
    st.subheader(f"Łączna liczba pozycji w magazynie: {len(st.session_state['towary'])}")
    
    # Wyświetlenie tabeli
    st.dataframe(df, hide_index=True)
else:
    st.warning("Magazyn jest pusty!")

st.markdown("---")
st.caption("Prosty Magazyn Streamlit by AI")
