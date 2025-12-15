import streamlit as st
import pandas as pd
from collections import Counter

# --- Konfiguracja Strony ---
st.set_page_config(layout="wide", page_title="Magazyn Pro z Ilościami")

# --- Inicjalizacja Stanu Sesji ---
if 'towary' not in st.session_state:
    st.session_state['towary'] = []

# --- Funkcje do Zarządzania Magazynem ---

def dodaj_towar(nazwa, ilosc):
    """Dodaje towar do listy w określonej ilości."""
    if nazwa and nazwa.strip():
        if ilosc < 1:
            st.warning("Ilość musi być większa niż zero.")
            return

        towar_czysty = nazwa.strip()
        
        # Dodajemy towar do listy 'ilosc' razy
        for _ in range(ilosc):
            st.session_state['towary'].append(towar_czysty)
            
        st.success(f"Dodano **{ilosc}** sztuk towaru: **{towar_czysty}**")
    else:
        st.warning("Nazwa towaru nie może być pusta.")

def usun_towar(nazwa):
    """Usuwa pierwsze wystąpienie towaru z listy."""
    try:
        st.session_state['towary'].remove(nazwa)
        st.info(f"Usunięto **1** sztukę towaru: **{nazwa}**")
    except ValueError:
        st.error(f"Błąd: Nie znaleziono towaru o nazwie **{nazwa}** na liście.")

# --- Interfejs Użytkownika (Streamlit) ---

st.title("🚀 Magazyn Towarów v4.0 (z obsługą ilości)")
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

# 2. Sekcje Dodawania i Usuwania Towaru
st.header("⚙️ Zarządzanie Magazynem")
col_add, col_remove = st.columns(2)

# --- Dodawanie ---
with col_add:
    st.subheader("➕ Dodaj Towar")
    with st.form("form_dodawania", clear_on_submit=True):
        nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj_nazwa")
        
        # DODANO: Pole do wprowadzania ilości
        ilosc_towaru = st.number_input(
            "Ilość do Dodania", 
            min_value=1, 
            value=1, 
            step=1, 
            key="input_dodaj_ilosc"
        )
        
        submitted_add = st.form_submit_button("Dodaj Towar", type="primary")
        
        if submitted_add:
            # Przekazanie nazwy i ilości do funkcji
            dodaj_towar(nowy_towar, ilosc_towaru) 

# --- Usuwanie ---
with col_remove:
    st.subheader("➖ Usuń Towar (usuwa 1 sztukę)")
    if st.session_state['towary']:
        liczniki = Counter(st.session_state['towary'])
        # Tworzymy czytelną listę do wyboru
        opcje_do_usuniecia = sorted([f"{nazwa} (Dostępnych: {ilosc})" for nazwa, ilosc in liczniki.items()])
        
        with st.form("form_usuwania"):
            towar_info_do_usuniecia = st.selectbox(
                "Wybierz towar do usunięcia:",
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
        search_term = st.text_input("Szukaj nazwy towaru:", "").lower()
        
        # Filtracja danych
        df_filtered = df[df['Nazwa Towaru'].str.lower().str.contains(search_term, na=False)]
            
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
        use_container_width=True
    )
    
    st.markdown("### Wykres Ilości")
    st.bar_chart(df_filtered.set_index('Nazwa Towaru')['Ilość'])
    
else:
    st.warning("Magazyn jest pusty! Użyj sekcji Dodaj, aby zacząć.")

st.markdown("---")
st.caption("Prosty Magazyn Streamlit z dodatkami v4.0")
