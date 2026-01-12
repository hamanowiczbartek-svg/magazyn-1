import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Zarządzanie Produktami", layout="centered")

st.title("📦 System Zarządzania Bazą Danych")

tab1, tab2 = st.tabs(["➕ Dodaj Produkt", "📂 Dodaj Kategorię"])

# --- TAB 2: DODAWANIE KATEGORII ---
with tab2:
    st.header("Nowa Kategoria")
    with st.form("category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        
        submit_kat = st.form_submit_button("Zapisz kategorię")
        
        if submit_kat:
            if kat_nazwa:
                data = {"nazwa": kat_nazwa, "opis": kat_opis}
                try:
                    supabase.table("kategorie").insert(data).execute()
                    st.success(f"Dodano kategorię: {kat_nazwa}")
                except Exception as e:
                    st.error(f"Błąd: {e}")
            else:
                st.warning("Nazwa kategorii jest wymagana!")

# --- TAB 1: DODAWANIE PRODUKTU ---
with tab1:
    st.header("Nowy Produkt")
    
    # Pobieranie listy kategorii do selectboxa
    try:
        response = supabase.table("kategorie").select("id, nazwa").execute()
        kategorie_list = response.data
        # Tworzymy słownik {nazwa: id} dla łatwego wyboru
        kat_options = {k['nazwa']: k['id'] for k in kategorie_list}
    except Exception as e:
        st.error("Nie udało się pobrać kategorii.")
        kat_options = {}

    with st.form("product_form", clear_on_submit=True):
        prod_nazwa = st.text_input("Nazwa produktu")
        prod_liczba = st.number_input("Liczba (ilość)", min_value=0, step=1)
        prod_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
        prod_kat_nazwa = st.selectbox("Kategoria", options=list(kat_options.keys()))
        
        submit_prod = st.form_submit_button("Zapisz produkt")
        
        if submit_prod:
            if prod_nazwa and prod_kat_nazwa:
                prod_data = {
                    "nazwa": prod_nazwa,
                    "liczba": int(prod_liczba),
                    "cena": float(prod_cena),
                    "kategoria_id": kat_options[prod_kat_nazwa]
                }
                try:
                    supabase.table("produkty").insert(prod_data).execute()
                    st.success(f"Dodano produkt: {prod_nazwa}")
                except Exception as e:
                    st.error(f"Błąd: {e}")
            else:
                st.warning("Wypełnij wszystkie pola!")

# Podgląd danych na dole
if st.checkbox("Pokaż aktualną listę produktów"):
    res = supabase.table("produkty").select("nazwa, liczba, cena, kategoria_id").execute()
    st.table(res.data)
