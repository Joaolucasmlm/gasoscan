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
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    st.session_state.ocr = GasoOCR(api_key=api_key)
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = AcidBaseAnalyzer()

st.title("🩸 GasoScan")
st.markdown("### Interpretador de Gasometria Avançado")

# ESCOLHA DO MÉTODO DE ENTRADA
input_method = st.radio(
    "Como deseja inserir os dados do exame?",
    ["📸 Ler laudo com IA", "⌨️ Digitar Manualmente"],
    horizontal=True
)

st.divider()

data = {} 

if input_method == "📸 Ler laudo com IA":
    uploaded_file = st.file_uploader("Suba a foto do laudo (Word, impresso ou tela)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        with st.spinner('Analisando laudo com IA...'):
            data, raw_text = st.session_state.ocr.scan_image(uploaded_file)
            
        with st.expander("🔍 Ver retorno da IA (Debug)"):
            st.write(f"```json\n{raw_text}\n```")
else:
    st.info("💡 Preencha os valores diretamente nos campos abaixo.")

# CAMPOS DE ENTRADA
st.subheader("Valores da Gasometria")
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

# MOTOR CLÍNICO
if st.button("🚀 Gerar Análise Completa", use_container_width=True):
    with st.spinner('Calculando distúrbios e etiologias...'):
        results = st.session_state.analyzer.analyze(ph, pco2, hco3, na, cl)
        
        st.divider()
        st.subheader("Resultado do Diagnóstico")
        
        st.write(f"**Status Inicial:** {results.get('status', '')}")

        primary = results.get("primary", "")
        if "Acidose" in primary:
            st.error(f"**Distúrbios Identificados:** {primary}")
        elif "Alcalose" in primary:
            st.warning(f"**Distúrbios Identificados:** {primary}")
        elif primary:
            st.info(f"**Distúrbios Identificados:** {primary}")
        else:
            st.success("**Status:** Normal")

        conclusion = results.get("conclusion", "")
        if conclusion:
            if "✅" in conclusion:
                st.success(conclusion)
            elif "❌" in conclusion:
                st.error(conclusion)
            else:
                st.info(conclusion)
                
        # Exibição dinâmica das Etiologias
        causas = results.get("causes", {})
        if causas:
            st.divider()
            st.subheader("📚 Investigação Etiológica")
            st.caption("Principais causas associadas aos distúrbios encontrados neste paciente:")
            
            for disturbio, lista_causas in causas.items():
                with st.expander(f"Causas de {disturbio}", expanded=True):
                    for causa in lista_causas:
                        st.markdown(f"- {causa}")
            
st.sidebar.markdown("---")
st.sidebar.caption("GasoScan v4.0 | Cronicidade, Compensação e Etiologias Integradas")
