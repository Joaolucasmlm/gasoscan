import google.generativeai as genai
import json
from PIL import Image

class GasoOCR:
    def __init__(self, api_key):
        # Autentica com a chave que está nos Secrets
        genai.configure(api_key=api_key)
        # Modelo mais rápido e inteligente para visão
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def scan_image(self, image_bytes):
        img = Image.open(image_bytes)
        
        prompt = """
        Você é um assistente médico especialista em gasometria.
        Analise a imagem deste laudo laboratorial e extraia os valores numéricos exatos de:
        - pH
        - pCO2
        - HCO3 (ou BIC/Bicarbonato)
        - Sódio (Na)
        - Cloro (Cl)
        
        Retorne APENAS um objeto JSON válido. Use letras minúsculas para as chaves (ph, pco2, hco3, na, cl).
        Os valores devem ser do tipo float. Substitua vírgulas por pontos se necessário.
        Se não achar um valor, não inclua a chave. 
        NÃO escreva nenhuma palavra antes ou depois do JSON.
        """
        
        try:
            # Envia o prompt e a imagem para o Gemini
            response = self.model.generate_content([prompt, img])
            raw_text = response.text
            
            # Limpa formatações markdown residuais
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            extracted = json.loads(clean_json)
            
            return extracted, raw_text
            
        except Exception as e:
            return {}, f"Erro na leitura da IA: {str(e)}"