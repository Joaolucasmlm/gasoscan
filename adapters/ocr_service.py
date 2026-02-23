import easyocr
import re
import numpy as np
from PIL import Image, ImageOps

class GasoOCR:
    def __init__(self):
        """
        Inicializa o motor de OCR otimizado para nuvem.
        Usa 'pt' e 'en' para cobrir termos técnicos e desativa GPU para economizar RAM.
        """
        self.reader = easyocr.Reader(['pt', 'en'], gpu=False)
        
    def scan_image(self, image_bytes):
        """
        Processa a imagem, melhora o contraste e extrai o texto bruto e os valores.
        """
        # Carrega e melhora a imagem para o OCR
        img = Image.open(image_bytes)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Converte para tons de cinza e melhora contraste (ajuda em fotos de hospital)
        img_processed = ImageOps.autocontrast(img.convert('L'))
        
        # Redimensiona para evitar o crash de 1GB de RAM no Streamlit Cloud
        img_processed.thumbnail((1200, 1200)) 
        
        img_np = np.array(img_processed)
        
        # Realiza a leitura do texto
        result = self.reader.readtext(img_np, detail=0)
        
        # Normaliza o texto bruto (minúsculo e remove espaços extras)
        full_text = " ".join(result).lower().strip()
        
        # Retorna o dicionário de valores e o texto bruto para debug
        return self._parse_values(full_text), full_text

    def _parse_values(self, text):
        """
        Mapeia siglas médicas para valores numéricos usando expressões regulares flexíveis.
        """
        # Padrões que aceitam variações de nomes, sinais (+/-) e separadores (vírgula/ponto/espaço)
        patterns = {
            # pH: aceita pH ou ph
            "ph": r"ph\s*[:=]?\s*(\d+[\.\s,]\d+)",
            
            # pCO2: aceita pCO2, PCO2, pCO2(c) ou pCO2(t)
            "pco2": r"(?:pco2|pco2\(c\)|pco2\(t\))\s*[:=]?\s*(\d+[\.\s,]\d*)",
            
            # HCO3: aceita HCO3, HCO3-, BIC ou Bicarbonato
            "hco3": r"(?:hco3|hco3-|bic|bicarbonato)\s*[:=]?\s*(\d+[\.\s,]\d*)",
            
            # Sódio: aceita Na, Na+, Sódio ou Sodio
            "na": r"(?:na|na\+|sódio|sodio)\s*[:=]?\s*(\d+[\.\s,]\d*)",
            
            # Cloro: aceita Cl, Cl- ou Cloro
            "cl": r"(?:cl|cl-|cloro)\s*[:=]?\s*(\d+[\.\s,]\d*)",
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                # Limpeza do valor: troca vírgula ou espaço por ponto para converter em float
                val_str = match.group(1).replace(",", ".").replace(" ", ".")
                try:
                    extracted[key] = float(val_str)
                except ValueError:
                    continue
                    
        return extracted