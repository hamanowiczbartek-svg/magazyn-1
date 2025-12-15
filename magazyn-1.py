import streamlit as st
import pandas as pd
from collections import Counter

# --- Konfiguracja Strony ---
st.set_page_config(layout="wide", page_title="Magazyn Pro")

# --- Inicjalizacja Stanu Sesji ---
if 'towary' not in st.session_state:
    st.session_state['towary'] = []

# --- Funkcje do Zarządzania Magazynem ---

def dodaj_towar(nazwa):
    """Dodaje towar do listy."""
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

st.title("🚀 Magazyn Towarów v3.0 z Dashboardem")
st.markdown("Aplikacja używa sesyjnego stanu. Dane **zostaną utracone** po odświeżeniu/zamknięciu.")

# 1. Wskaźniki/Statystyki (Metrics)
if st.session_state['towary']:
    unikalne_pozycje = len(set(st.session_state['towary']))
    laczna_ilosc = len(st.session_state['towary'])
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Unikalne Typy Towarów", unikalne_pozycje)
    col2.metric("Łączna Ilość w Magazynie", laczna_ilosc)
    
    # Obliczanie najczęściej występującego towaru
    najczesciej = Counter(st.session_state['towary']).most_common(1)
    if najczesciej:
         col3.metric("Najczęściej Występujący", f"{najczesciej[0][0]}", f"Ilość: {najczesciej[0][1]}")
    else:
         col3.metric("Najczęściej Występujący", "Brak")
         
st.markdown("---")

# 2. Sekcje Dodawania i Usuwania Towaru (Ułożone w kolumnach)
st.header("⚙️ Zarządzanie Magazynem")
col_add, col_remove = st.columns(2)

# --- Dodawanie ---
with col_add:
    st.subheader("➕ Dodaj")
    with st.form("form_dodawania", clear_on_submit=True):
        nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj_v3")
        submitted_add = st.form_submit_button("Dodaj Towar", type="primary")
        
        if submitted_add:
            dodaj_towar(nowy_towar) 

# --- Usuwanie ---
with col_remove:
    st.subheader("➖ Usuń")
    if st.session_state['towary']:
        liczniki = Counter(st.session_state['towary'])
        # Tworzymy czytelną listę do wyboru
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

# 3. Sekcja Wyświetlania i Filtrowania Stanu Magazynu
st.header("📋 Szczegółowy Stan Magazynu")

if st.session_state['towary']:
    # Tworzenie DataFrame z danymi
    liczniki_final = Counter(st.session_state['towary'])
    dane_do_tabeli = [
        {"Nazwa Towaru": nazwa, "Ilość": ilosc} 
        for nazwa, ilosc in sorted(liczniki_final.items())
    ]
    df = pd.DataFrame(dane_do_tabeli)
    
    # Dodanie paska bocznego do filtrowania
    with st.sidebar:
        st.header("🔎 Filtrowanie")
        
        # Opcja wyszukiwania tekstowego
        search_term = st.text_input("Szukaj nazwy towaru:", "").lower()
        
        # Filtracja danych
        if search_term:
            df_filtered = df[df['Nazwa Towaru'].str.lower().str.contains(search_term, na=False)]
        else:
            df_filtered = df
            
        # Opcjonalny suwak do filtrowania ilości
        min_ilosc, max_ilosc = int(df['Ilość'].min()), int(df['Ilość'].max())
        ilosc_zakres = st.slider(
            "Filtruj wg Ilości:",
            min_value=min_ilosc,
            max_value=max_ilosc,
            value=(min_ilosc, max_ilosc)
        )
        
        df_filtered = df_filtered[
            (df_filtered['Ilość'] >= ilosc_zakres[0]) & 
            (df_filtered['Ilość'] <= ilosc_zakres[1])
        ]
        
    st.subheader(f"Wyświetlane pozycje: {len(df_filtered)}")
    
    # Wyświetlenie tabeli z możliwością interakcji
    st.dataframe(
        df_filtered, 
        hide_index=True, 
        use_container_width=True # Pełna szerokość kontenera
    )
    
    st.markdown("### Wykres Ilości")
    # Wizualizacja danych na wykresie słupkowym
    st.bar_chart(df_filtered.set_index('Nazwa Towaru')['Ilość'])
    
else:
    st.warning("Magazyn jest pusty! Użyj sekcji Dodaj, aby zacząć.")

st.markdown("---")
st.caption("Prosty Magazyn Streamlit z dodatkami v3.0")
