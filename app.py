from html.parser import HTMLParser
from urllib.parse import urljoin
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Marktplaats & Veiling Tool-Suite",
    layout="wide",
    page_icon="🚀",
)


# Eenvoudige, ingebouwde HTML Link Extractor (geen externe bs4 nodig)
class SimpleLinkParser(HTMLParser):

  def __init__(self, base_url):
    super().__init__()
    self.base_url = base_url
    self.links = set()

  def handle_starttag(self, tag, attrs):
    if tag == "a":
      for attr, value in attrs:
        if attr == "href" and value:
          full_url = urljoin(self.base_url, value)
          self.links.add(full_url)


# Zijbalk Navigatie
st.sidebar.title("📌 Navigatie")
app_mode = st.sidebar.selectbox(
    "Kies een tool",
    [
        "🔨 Veiling Arbitrage & Filter Tool",
        "📦 Marktplaats Bulk Manager",
        "🔗 Webpagina Link Scraper",
    ],
)

# ==========================================
# TOOL 1: VEILING ARBITRAGE & FILTER TOOL
# ==========================================
if app_mode == "🔨 Veiling Arbitrage & Filter Tool":
  st.title("🔨 Veiling Arbitrage & Filter Tool")
  st.caption("Analyseer en filter veilingkavels op winstgevendheid")

  st.sidebar.header("⚙️ Veiling Instellingen")
  gewenste_marge = (
      st.sidebar.slider(
          "Beoogde Winstmarge (%)",
          min_value=20,
          max_value=150,
          value=60,
          step=5,
      )
      / 100.0
  )
  kosten_factor = st.sidebar.number_input(
      "Veilingkosten Factor (Opgeld + BTW)",
      min_value=1.10,
      max_value=1.80,
      value=1.45,
      step=0.01,
  )

  tab1, tab2 = st.tabs(
      ["🧮 Snelle Kavel Berekening", "📊 Bulk Link & Batch Filter"]
  )

  with tab1:
    st.subheader("Analyseer 1 Specifiek Kavel")
    col1, col2 = st.columns(2)

    with col1:
      item_naam = st.text_input(
          "Naam van het item/kavel", "DeWalt Accuboormachine Set 18V"
      )
      veiling_link = st.text_input(
          "Veiling Link (URL)", "https://www.troostwijkauctions.com/..."
      )
      categorie = st.selectbox(
          "Categorie",
          [
              "Gereedschap & Bouw",
              "Elektronica & Audio",
              "Fietsen & Transport",
              "Horeca & Keuken",
              "Kantoorinrichting & Meubels",
              "Overig",
          ],
      )
      conditie = st.selectbox(
          "Conditie op veiling",
          [
              "Nieuw / Retourgoed",
              "Gebruikt (Werkend)",
              "Ongetest / Schade",
              "Incompleet / Defect",
          ],
      )

    with col2:
      nieuwprijs = st.number_input(
          "Nieuwprijs / Winkelwaarde (€)", min_value=0.0, value=250.0, step=10.0
      )
      resale_prijs = st.number_input(
          "Realistische Tweedehands Waarde (€)",
          min_value=0.0,
          value=150.0,
          step=5.0,
      )

    pop_map = {
        "Gereedschap & Bouw": ("🔥 Hoog", "1 - 7 dagen", 2),
        "Elektronica & Audio": ("🔥 Hoog", "3 - 10 dagen", 4),
        "Fietsen & Transport": ("🔥 Hoog", "1 - 7 dagen", 2),
        "Horeca & Keuken": ("⚠️ Matig", "14 - 30 dagen", 5),
        "Kantoorinrichting & Meubels": ("⚠️ Laag", "30 - 60+ dagen", 6),
        "Overig": ("⚠️ Matig", "14 - 30 dagen", 4),
    }

    pop_nl, levertijd_nl, base_risk = pop_map[categorie]
    if conditie == "Ongetest / Schade":
      base_risk += 3
    elif conditie == "Incompleet / Defect":
      base_risk += 4
    base_risk = min(base_risk, 10)

    max_totale_kosten = resale_prijs / (1.0 + gewenste_marge)
    max_bod = max_totale_kosten / kosten_factor
    veilingkosten = max_bod * (kosten_factor - 1.0)
    netto_winst = resale_prijs - max_totale_kosten
    korting_op_nieuw = (
        ((nieuwprijs - max_totale_kosten) / nieuwprijs * 100)
        if nieuwprijs > 0
        else 0
    )

    st.markdown("### 🎯 Resultaat & Biedadvies")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("🔨 Maximaal Bod", f"€{max_bod:.2f}")
    res_col2.metric(
        f"💸 Veilingkosten (x{kosten_factor})", f"€{veilingkosten:.2f}"
    )
    res_col3.metric("💰 Totale Inkoop", f"€{max_totale_kosten:.2f}")
    res_col4.metric("📈 Netto Winst", f"€{netto_winst:.2f}")

    if veiling_link:
      st.markdown(f"[🔗 Direct naar Veilingkavel]({veiling_link})")

  with tab2:
    st.subheader("Bulk Veiling Filter via CSV")
    uploaded_file = st.file_uploader(
        "Upload CSV met kolommen: link, titel, nieuwprijs, resale_waarde,"
        " categorie",
        type=["csv"],
    )

    if uploaded_file:
      df_veiling = pd.read_csv(uploaded_file)
      df_veiling["Max Totale Inkoop"] = df_veiling["resale_waarde"] / (
          1.0 + gewenste_marge
      )
      df_veiling["Max Bod"] = df_veiling["Max Totale Inkoop"] / kosten_factor
      df_veiling["Veilingkosten"] = df_veiling["Max Bod"] * (
          kosten_factor - 1.0
      )
      df_veiling["Netto Winst"] = (
          df_veiling["resale_waarde"] - df_veiling["Max Totale Inkoop"]
      )

      min_winst = st.slider("Filter op minimale netto winst (€)", 0, 200, 25)
      filtered_df = df_veiling[df_veiling["Netto Winst"] >= min_winst]

      st.write(
          f"### Gefilterde Rendabele Kavels ({len(filtered_df)} van"
          f" {len(df_veiling)} items):"
      )
      st.dataframe(filtered_df, use_container_width=True)

      csv_data = filtered_df.to_csv(index=False).encode("utf-8")
      st.download_button(
          "📥 Download Gefilterde Rendabele Kavels",
          csv_data,
          "rendabele_veiling_kavels.csv",
          "text/csv",
      )

# ==========================================
# TOOL 2: MARKTPLAATS BULK MANAGER
# ==========================================
elif app_mode == "📦 Marktplaats Bulk Manager":
  st.title("📦 Marktplaats Bulk Manager")
  st.markdown(
      "Upload je CSV-bestand met advertenties om ze eenvoudig door te lopen en"
      " te plaatsen."
  )

  uploaded_file_mp = st.file_uploader(
      "Upload je CSV-bestand (titel, beschrijving, prijs)", type=["csv"]
  )

  if uploaded_file_mp is not None:
    df_mp = pd.read_csv(uploaded_file_mp)
    st.success(f"Succesvol {len(df_mp)} advertenties geladen!")

    st.subheader("📋 Overzicht van je advertenties")
    st.dataframe(df_mp, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Advertentie voor advertentie doorlopen")

    if "index" not in st.session_state:
      st.session_state.index = 0

    if len(df_mp) > 0:
      current_idx = st.session_state.index
      row = df_mp.iloc[current_idx]

      st.info(f"Advertentie {current_idx + 1} van {len(df_mp)}")

      titel = st.text_input("Titel", value=str(row.get("titel", "")))
      prijs = st.text_input("Prijs (€)", value=str(row.get("prijs", "")))
      beschrijving = st.text_area(
          "Beschrijving", value=str(row.get("beschrijving", ""))
      )

      col_prev, col_next = st.columns(2)
      with col_prev:
        if st.button("⬅️ Vorige") and st.session_state.index > 0:
          st.session_state.index -= 1
          st.rerun()
      with col_next:
        if (
            st.button("Volgende ➡️")
            and st.session_state.index < len(df_mp) - 1
        ):
          st.session_state.index += 1
          st.rerun()

      st.markdown("---")
      st.markdown(
          "[🔗 Open Marktplaats"
          " Plaatsingspagina](https://www.marktplaats.nl/m/my-account/sell/index.html)"
      )

# ==========================================
# TOOL 3: WEBPAGINA LINK SCRAPER
# ==========================================
elif app_mode == "🔗 Webpagina Link Scraper":
  st.title("🔗 Webpagina Link Scraper")
  st.caption(
      "Haal alle links op van een statische webpagina zonder externe pakketten"
  )

  url_input = st.text_input(
      "Voer de URL in van de pagina die je wilt scrappen:",
      "https://example.com",
  )

  if st.button("Start Scrappen"):
    if url_input:
      with st.spinner("Bezig met ophalen van links..."):
        try:
          headers = {
              "User-Agent": (
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
                  " Safari/537.36"
              )
          }
          response = requests.get(url_input, headers=headers, timeout=10)

          if response.status_code == 200:
            parser = SimpleLinkParser(url_input)
            parser.feed(response.text)

            found_links = sorted(list(parser.links))
            st.success(f"Totaal {len(found_links)} unieke links gevonden!")
            for idx, link in enumerate(found_links, 1):
              st.write(f"{idx}. [{link}]({link})")
          else:
            st.error(
                "Kan pagina niet bereiken. Statuscode:"
                f" {response.status_code}"
            )
        except Exception as e:
          st.error(f"Er is een fout opgetreden: {str(e)}")
