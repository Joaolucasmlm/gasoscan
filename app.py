import streamlit as st
from domain.models import BloodGasData
from core.analyzers.acid_base import AcidBaseAnalyzer
from adapters.ocr_service import GasoOCR

# Configuração da página para aproveitar o hardware do seu Ryzen 5
st.set_page_config(page_title="GasoScan Pro OCR", layout="wide", page_icon="🩸")

st.title("🩸 GasoScan: Inteligência Clínica")
st.markdown("---")

# Inicializa o motor de OCR (Cache para não recarregar a cada clique)
@st.cache_resource
def load_ocr():
    return GasoOCR()

ocr_engine = load_ocr()

# 1. Seção de Upload de Imagem (Visão Computacional)
st.subheader("📷 Entrada de Dados: Foto do Laudo")
uploaded_file = st.file_uploader("Suba o print ou foto da gasometria", type=['png', 'jpg', 'jpeg'])

# Dicionário para armazenar valores lidos pela IA
ocr_values = {}

if uploaded_file:
    with st.spinner("IA processando o laudo..."):
        try:
            ocr_values = ocr_engine.scan_image(uploaded_file)
            if ocr_values:
                st.success("✅ Valores extraídos com sucesso! Confira na barra lateral.")
            else:
                st.warning("⚠️ Não identifiquei valores claros. Verifique a iluminação da foto.")
        except Exception as e:
            st.error(f"Erro no processamento da imagem: {e}")

# 2. Formulário de Dados na Barra Lateral (Sidebar)
with st.sidebar:
    st.header("📋 Parâmetros Clínicos")
    
    # Preenche automaticamente com o que a IA leu, ou usa os padrões
    ph = st.number_input("pH", 6.8, 7.8, ocr_values.get("ph", 7.40), 0.01, format="%.2f")
    pco2 = st.number_input("pCO2 (mmHg)", 10.0, 130.0, ocr_values.get("pco2", 40.0), 0.1)
    hco3 = st.number_input("HCO3- (mEq/L)", 5.0, 50.0, ocr_values.get("hco3", 24.0), 0.1)
    
    st.markdown("---")
    st.header("🧪 Eletrólitos (Opcional)")
    # Se a IA não ler, o campo fica vazio para preenchimento manual
    na = st.number_input("Sódio (Na+)", value=ocr_values.get("na"))
    cl = st.number_input("Cloro (Cl-)", value=ocr_values.get("cl"))
    alb = st.number_input("Albumina (g/dL)", value=4.5)

# 3. Execução da Análise Clínica
if st.button("Executar Análise Clínica", type="primary"):
    try:
        # Cria o objeto de dados com as validações do Pydantic
        data = BloodGasData(ph=ph, pco2=pco2, hco3=hco3, na=na, cl=cl, albumina=alb)
        
        # Chama o analisador profissional
        analyzer = AcidBaseAnalyzer(data)
        result = analyzer.analyze()
        
        st.markdown("### 📋 Diagnóstico Final")
        
        # Exibe os distúrbios com cores diferenciadas
        for d in result['disorders']:
            if "Normal" in d:
                st.success(f"✅ **{d}**")
            else:
                st.error(f"🚨 **{d}**")
        
        # Exibe notas de cálculo (Anion Gap, Delta/Delta, etc.)
        if result['notes']:
            with st.expander("💡 Notas de Interpretação e Cálculos", expanded=True):
                for n in result['notes']:
                    st.write(f"- {n}")
                    
    except Exception as e:
        st.error(f"🚨 Erro na validação: {e}")

# Rodapé com status do sistema
st.markdown("---")
st.caption("GasoScan v1.0 - Desenvolvido para auxílio diagnóstico clínico.")