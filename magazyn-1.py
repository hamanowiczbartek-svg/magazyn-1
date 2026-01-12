import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
try:
    # Pobieranie danych z secrets (upewnij się, że są w Streamlit Cloud lub .streamlit/secrets.toml)
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"❌ Błąd konfiguracji kluczy: {e}")
    st.stop()

st.title("Zarządzanie Produktami")

# --- FUNKCJE POBIERANIA DANYCH ---
def pobierz_kategorie():
    try:
        # Pobieramy dane i wymuszamy listę słowników
        odpowiedz = supabase.table("kategorie").select("*").execute()
        return odpowiedź.data
    except Exception as e:
        st.error(f"❌ Nie udało się pobrać kategorii z bazy: {e}")
        return []

# --- INTERFEJS ---
zakladka_produkty, zakladka_kategorie = st.tabs(["Dodaj Produkt", "Dodaj Kategorię"])

# 📂 DODAWANIE KATEGORII
with zakladka_kategorie:
    st.subheader("Nowa Kategoria")
    with st.form("form_kat"):
        n_kat = st.text_input("Nazwa kategorii")
        o_kat = st.text_area("Opis kategorii")
        btn_kat = st.form_submit_button("Zapisz kategorię")
        
        if btn_kat:
            if n_kat:
                res = supabase.table("kategorie").insert({"nazwa": n_kat, "opis": o_kat}).execute()
                st.success("✅ Kategoria dodana!")
                st.rerun()
            else:
                st.warning("Wpisz nazwę!")

# ➕ DODAWANIE PRODUKTU
with zakladka_produkty:
    st.subheader("Nowy Produkt")
    
    lista_kat = pobierz_kategorie()
    
    if not lista_kat:
        st.info("Baza kategorii jest pusta. Dodaj najpierw kategorię w drugiej zakładce.")
    else:
        # Przygotowanie listy do wyboru
        opcje_kat = {item['nazwa']: item['id'] for item in lista_kat}
        
        with st.form("form_prod"):
            n_prod = st.text_input("Nazwa produktu")
            l_prod = st.number_input("Ilość (liczba)", min_value=0, step=1)
            c_prod = st.number_input("Cena", min_value=0.0)
            k_prod_nazwa = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
            
            btn_prod = st.form_submit_button("Zapisz produkt")
            
            if btn_prod:
                if n_prod:
                    dane = {
                        "nazwa": n_prod,
                        "liczba": int(l_prod),
                        "cena": float(c_prod),
                        "kategoria_id": opcje_kat[k_prod_nazwa]
                    }
                    try:
                        supabase.table("produkty").insert(dane).execute()
                        st.success(f"✅ Produkt {n_prod} dodany!")
                    except Exception as e:
                        st.error(f"Błąd Supabase: {e}")
                else:
                    st.warning("Wpisz nazwę produktu!")

# --- PODGLĄD DANYCH (DEBUG) ---
with st.expander("Podgląd bazy (Debug)"):
    if st.button("Odśwież tabele"):
        kat = supabase.table("kategorie").select("*").execute()
        prod = supabase.table("produkty").select("*").execute()
        st.write("Kategorie w bazie:", kat.data)
        st.write("Produkty w bazie:", prod.data)
