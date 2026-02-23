import streamlit as st
from adapters.ocr_service import GasoOCR
from core.analyzers.acid_base import AcidBaseAnalyzer

# Configuração da página
st.set_page_config(
    page_title="GasoScan | Clinical Analysis", 
    page_icon="🩸", 
    layout="centered"
)

# Inicialização dos motores
if 'ocr' not in st.session_state:
    st.session_state.ocr = GasoOCR()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = AcidBaseAnalyzer()

st.title("🩸 GasoScan")
st.markdown("### Interpretador de Gasometria com Visão Computacional")
st.info("Desenvolvido para suporte à decisão clínica no internato.")

uploaded_file = st.file_uploader("Suba a foto do laudo (pH, pCO2, BIC, Na, Cl)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    with st.spinner('IA lendo o laudo... (pode demorar alguns segundos na nuvem)'):
        data, raw_text = st.session_state.ocr.scan_image(uploaded_file)
        
    with st.expander("🔍 Ver texto bruto extraído pela IA (Debug)"):
        st.write(f"O que a IA leu: `{raw_text}`")
        st.caption("Se algum valor não foi identificado, verifique se a sigla apareceu corretamente aqui.")

    st.subheader("Confirme os Valores")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ph = st.number_input("pH", value=data.get("ph", 7.40), step=0.01, format="%.2f")
    with col2:
        pco2 = st.number_input("pCO2", value=data.get("pco2", 40.0), step=1.0)
    with col3:
        hco3 = st.number_input("HCO3 (BIC)", value=data.get("hco3", 24.0), step=1.0)

    col4, col5 = st.columns(2)
    with col4:
        na = st.number_input("Sódio (Na+)", value=data.get("na", 140.0), step=1.0)
    with col5:
        cl = st.number_input("Cloro (Cl-)", value=data.get("cl", 104.0), step=1.0)

    if st.button("🚀 Gerar Análise Completa"):
        with st.spinner('Calculando distúrbios e compensações...'):
            results = st.session_state.analyzer.analyze(ph, pco2, hco3, na, cl)
            
            st.divider()
            st.subheader("Resultado do Diagnóstico")
            
            if "Acidose" in results.get("primary", ""):
                st.error(f"**{results['primary']}**")
            elif "Alcalose" in results.get("primary", ""):
                st.warning(f"**{results['primary']}**")
            else:
                st.success(f"**Status: {results['status']}**")

            # Exibe a fórmula de Winter, se houver
            if results.get("compensation"):
                st.info(results["compensation"])

            # Exibe o Delta/Delta, se houver
            if results.get("delta_delta"):
                st.info(results["delta_delta"])
                st.caption("Análise de distúrbios triplos baseada na relação $\Delta AG / \Delta HCO_3$.")

st.sidebar.markdown("---")
st.sidebar.caption("GasoScan v1.0 | Desenvolvido para pesquisa médica e prática clínica.")