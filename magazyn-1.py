import streamlit as st
from supabase import create_client, Client

# 1. Połączenie z bazą
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Błąd konfiguracji Secrets! Sprawdź czy dodałeś SUPABASE_URL i KEY.")
    st.stop()

st.title("📦 Zarządzanie Magazynem")

# Funkcja pomocnicza do pobierania kategorii
def get_categories():
    try:
        # Pobieramy ID i Nazwę
        response = supabase.table("kategorie").select("id, nazwa").execute()
        return response.data
    except Exception as e:
        st.error(f"Nie udało się pobrać kategorii: {e}")
        return []

tab1, tab2 = st.tabs(["➕ Dodaj Produkt", "📂 Dodaj Kategorię"])

# --- TAB 2: DODAWANIE KATEGORII ---
with tab2:
    st.header("Dodaj nową kategorię")
    with st.form("category_form"):
        kat_nazwa = st.text_input("Nazwa kategorii (np. Elektronika)")
        kat_opis = st.text_area("Opis kategorii")
        submit_kat = st.form_submit_button("Zapisz kategorię")
        
        if submit_kat:
            if kat_nazwa.strip():
                res = supabase.table("kategorie").insert({"nazwa": kat_nazwa, "opis": kat_opis}).execute()
                st.success(f"Dodano kategorię: {kat_nazwa}")
                st.rerun() # Odświeżamy aplikację, by kategoria pojawiła się w liście produktów
            else:
                st.error("Nazwa kategorii nie może być pusta!")

# --- TAB 1: DODAWANIE PRODUKTU ---
with tab1:
    st.header("Dodaj nowy produkt")
    
    kategorie = get_categories()
    
    if not kategorie:
        st.warning("⚠️ Brak kategorii w bazie! Najpierw dodaj kategorię w drugiej zakładce.")
    else:
        # Tworzymy opcje do wyboru: "Nazwa (ID)"
        options = {k['nazwa']: k['id'] for k in kategorie}
        
        with st.form("product_form"):
            prod_nazwa = st.text_input("Nazwa produktu")
            prod_liczba = st.number_input("Ilość", min_value=0, step=1)
            prod_cena = st.number_input("Cena (użyj kropki zamiast przecinka)", min_value=0.0, step=0.01)
            
            # Kluczowy moment: Wybór kategorii
            wybrana_kat_nazwa = st.selectbox("Wybierz kategorię", options=list(options.keys()))
            
            submit_prod = st.form_submit_button("Dodaj produkt do bazy")
            
            if submit_prod:
                if prod_nazwa.strip():
                    new_product = {
                        "nazwa": prod_nazwa,
                        "liczba": int(prod_liczba),
                        "cena": float(prod_cena),
                        "kategoria_id": options[wybrana_kat_nazwa]
                    }
                    try:
                        supabase.table("produkty").insert(new_product).execute()
                        st.success(f"Produkt '{prod_nazwa}' został dodany!")
                    except Exception as e:
                        st.error(f"Błąd zapisu: {e}")
                else:
                    st.error("Nazwa produktu jest wymagana!")

---
### Dlaczego wcześniej mogło nie działać? (Lista kontrolna)

1.  **Pusta tabela kategorii**: Jeśli nie dodałeś najpierw kategorii w Supabase, `selectbox` nie miał co wyświetlić. W tym kodzie dodałem `st.rerun()`, który wymusza odświeżenie listy zaraz po dodaniu nowej kategorii.
2.  **Uprawnienia RLS (Row Level Security)**: W panelu Supabase sprawdź, czy Twoje tabele mają wyłączone RLS, lub czy dodałeś politykę pozwalającą na `INSERT` i `SELECT`. Jeśli RLS jest włączone i nie ma polityk, Python nie "zobaczy" danych.
3.  **Typy danych**: Supabase jest rygorystyczny. Jeśli w bazie masz `int8`, a Python wyśle `string`, wyrzuci błąd. W powyższym kodzie wymusiłem `int()` i `float()`.

**Czy po dodaniu pierwszej kategorii w zakładce "Dodaj Kategorię" lista w "Dodaj Produkt" teraz się pojawia?**
