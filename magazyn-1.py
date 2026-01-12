import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

# 1. Konfiguracja połączenia
conn = st.connection("supabase", type=SupabaseConnection)

st.title("📦 Zarządzanie Magazynem")

# --- MENU BOCZNE ---
menu = st.sidebar.selectbox("Wybierz akcję", ["Dodaj produkt", "Dodaj kategorię", "Lista produktów"])

# --- FUNKCJA POBIERANIA DANYCH ---
def get_data():
    # Pobieramy produkty razem z nazwą kategorii (join)
    res = conn.table("produkty").select("id, nazwa, liczba, cena, kategoria_id, kategorie(nazwa)").execute()
    return pd.DataFrame(res.data)

# --- SEKCJA: DODAWANIE KATEGORII ---
if menu == "Dodaj kategorię":
    st.header("Dodaj nową kategorię")
    with st.form("kat_form"):
        nowa_kat = st.text_input("Nazwa kategorii")
        opis = st.text_area("Opis (opcjonalnie)")
        if st.form_submit_button("Zapisz"):
            if nowa_kat:
                conn.table("kategorie").insert({"nazwa": nowa_kat, "opis": opis}).execute()
                st.success("Dodano kategorię!")
            else:
                st.error("Podaj nazwę!")

# --- SEKCJA: DODAWANIE PRODUKTU ---
elif menu == "Dodaj produkt":
    st.header("Dodaj nowy produkt")
    # Pobieramy kategorie, żeby użytkownik mógł wybrać z listy
    kat_res = conn.table("kategorie").select("id, nazwa").execute()
    kategorie = {item['nazwa']: item['id'] for item in kat_res.data}
    
    if not kategorie:
        st.warning("Najpierw dodaj kategorię!")
    else:
        with st.form("prod_form"):
            nazwa = st.text_input("Nazwa produktu")
            cena = st.number_input("Cena", min_value=0.0, format="%.2f")
            liczba = st.number_input("Ilość", min_value=0, step=1)
            kat_wybor = st.selectbox("Kategoria", list(kategorie.keys()))
            
            if st.form_submit_button("Dodaj produkt"):
                if nazwa:
                    conn.table("produkty").insert({
                        "nazwa": nazwa,
                        "cena": cena,
                        "liczba": liczba,
                        "kategoria_id": kategorie[kat_wybor]
                    }).execute()
                    st.success("Produkt dodany!")
                else:
                    st.error("Podaj nazwę produktu!")

# --- SEKCJA: LISTA I FILTROWANIE (TUTAJ BYŁ BŁĄD) ---
elif menu == "Lista produktów":
    st.header("Twoje produkty")
    df = get_data()

    if df.empty:
        st.info("Baza danych jest pusta.")
    else:
        # --- BEZPIECZNY SUWAK ---
        min_v = int(df["liczba"].min())
        max_v = int(df["liczba"].max())

        # Naprawa błędu: slider pokaże się tylko jeśli jest z czego wybierać
        if min_v < max_v:
            zakres = st.slider("Filtruj wg ilości", min_v, max_v, (min_v, max_v))
            df = df[(df["liczba"] >= zakres[0]) & (df["liczba"] <= zakres[1])]
        else:
            st.write(f"Wszystkie produkty mają taką samą ilość: **{min_v}**")

        # Wyświetlanie tabeli
        st.dataframe(df[["id", "nazwa", "cena", "liczba"]], use_container_width=True)
