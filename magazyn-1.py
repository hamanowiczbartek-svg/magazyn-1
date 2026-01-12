import streamlit as st

# --- Inicjalizacja Stanu Sesji ---
# Sprawdzamy, czy 'towary' już istnieją w stanie sesji. 
# Jeśli nie, inicjalizujemy pustą listę. To przechowuje nasze dane!
if 'towary' not in st.session_state:
    st.session_state['towary'] = []

# --- Funkcje do Zarządzania Magazynem ---

def dodaj_towar(nazwa):
    """Dodaje towar do listy."""
    if nazwa and nazwa.strip():  # Sprawdzamy, czy nazwa nie jest pusta
        st.session_state['towary'].append(nazwa.strip())
        st.success(f"Dodano towar: **{nazwa.strip()}**")
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

st.title("📦 Prosty Magazyn Towarów")
st.markdown("Aplikacja używa list w pamięci (sesyjny stan Streamlit). Dane **zostaną utracone** po odświeżeniu/zamknięciu.")

# 1. Sekcja Dodawania Towaru
st.header("➕ Dodaj Nowy Towar")
with st.form("form_dodawania"):
    nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj")
    submitted_add = st.form_submit_button("Dodaj")
    if submitted_add:
        dodaj_towar(nowy_towar)
        # Opcjonalnie: Umożliwia ponowne użycie formularza bez ponownego wpisywania
        st.session_state.input_dodaj = "" 

st.markdown("---")

# 2. Sekcja Usuwania Towaru
st.header("➖ Usuń Towar")

if st.session_state['towary']:
    # Tworzenie listy opcji do wyboru (usuwamy duplikaty, aby lista była czystsza)
    unikalne_towary = sorted(list(set(st.session_state['towary'])))
    
    with st.form("form_usuwania"):
        # Używamy selectbox, aby łatwo wybrać towar do usunięcia
        towar_do_usuniecia = st.selectbox(
            "Wybierz towar do usunięcia (usuwa **jedno** wystąpienie):",
            unikalne_towary,
            key="input_usun"
        )
        submitted_remove = st.form_submit_button("Usuń Wybrany Towar")

        if submitted_remove and towar_do_usuniecia:
            usun_towar(towar_do_usuniecia)
else:
    st.info("Brak towarów do usunięcia.")

st.markdown("---")

# 3. Sekcja Wyświetlania Stanu Magazynu
st.header("📋 Aktualny Stan Magazynu")

if st.session_state['towary']:
    # Obliczanie liczby wystąpień każdego towaru
    liczniki = {towar: st.session_state['towary'].count(towar) for towar in set(st.session_state['towary'])}
    
    # Wyświetlanie w formie tabeli lub listy
    st.subheader(f"Łączna liczba pozycji: {len(st.session_state['towary'])}")
    
    # Tworzenie czytelnej tabeli
    dane_do_tabeli = [{"Nazwa Towaru": nazwa, "Ilość": ilosc} for nazwa, ilosc in liczniki.items()]
    
    st.dataframe(dane_do_tabeli, hide_index=True)
else:
    st.warning("Magazyn jest pusty!")

# Mały separator na dole
st.markdown("---")
st.caption("Prosty Magazyn Streamlit by AI")
