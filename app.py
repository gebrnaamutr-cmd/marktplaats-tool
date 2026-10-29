import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marktplaats Bulk Manager", page_icon="📦", layout="centered")

st.title("📦 Marktplaats Bulk Manager")
st.markdown("Upload je CSV-bestand met advertenties om ze eenvoudig te beheren en te kopiëren voor plaatsing.")

# Bestand uploaden
uploaded_file = st.file_uploader("Upload je CSV-bestand (titel, beschrijving, prijs)", type=["csv"])

if uploaded_file is not None:
    # Lees CSV in
    df = pd.read_csv(uploaded_file)
    
    st.success(f"Succesvol {len(df)} advertenties geladen!")
    
    # Toon overzichtstabel
    st.subheader("📋 Overzicht van je advertenties")
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🚀 Advertentie voor advertentie doorlopen")
    
    # Sla de index op in de sessie om door advertenties te bladeren
    if 'index' not in st.session_state:
        st.session_state.index = 0
        
    if len(df) > 0:
        current_idx = st.session_state.index
        row = df.iloc[current_idx]
        
        st.info(f"Advertentie {current_idx + 1} van {len(df)}")
        
        # Velden tonen die je direct kunt kopiëren of aanpassen
        titel = st.text_input("Titel", value=str(row.get('titel', '')))
        prijs = st.text_input("Prijs (€)", value=str(row.get('prijs', '')))
        beschrijving = st.text_area("Beschrijving", value=str(row.get('beschrijving', '')), height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Vorige advertentie") and st.session_state.index > 0:
                st.session_state.index -= 1
                st.rerun()
        with col2:
            if st.button("Volgende advertentie ➡️") and st.session_state.index < len(df) - 1:
                st.session_state.index += 1
                st.rerun()
                
        # Directe link naar de Marktplaats plaatsingspagina
        st.markdown("---")
        st.markdown("[🔗 Open Marktplaats Plaatsingspagina](https://www.marktplaats.nl/s/plaats-advertentie)")
else:
    # Voorbeeld download om te tonen hoe het CSV-bestand eruit moet zien
    st.markdown("### Voorbeeld van je CSV-indeling:")
    st.code("titel,beschrijving,prijs\n\"Boekenmand van riet\",\"Handgemaakt, zo goed als nieuw.\",15.00\n\"Vintage bureaulamp\",\"Mooie gebruikte staat.\",25.00", language="csv") 