import easyocr
import re
import numpy as np
from PIL import Image

class GasoOCR:
    def __init__(self):
        # Inicializa o leitor em PT e EN. O Ryzen 5 carrega isso rápido.
        self.reader = easyocr.Reader(['pt', 'en'])
        
    def scan_image(self, image_bytes):
        """Converte imagem em texto e extrai os valores usando Regex."""
        # Converte para formato que o EasyOCR entende
        img = Image.open(image_bytes)
        img_np = np.array(img)
        
        # Realiza o OCR
        result = self.reader.readtext(img_np, detail=0)
        full_text = " ".join(result).replace(",", ".") # Normaliza vírgulas
        
        return self._parse_values(full_text)

    def _parse_values(self, text):
        """Busca padrões como 'pH 7.35' ou 'pCO2: 40' no texto bruto."""
        patterns = {
            "ph": r"ph\s*[:=]?\s*(\d+\.\d+)",
            "pco2": r"pco2\s*[:=]?\s*(\d+\.?\d*)",
            "hco3": r"hco3\s*[:=]?\s*(\d+\.?\d*)",
            "na": r"na\+?\s*[:=]?\s*(\d+\.?\d*)",
            "cl": r"cl-?\s*[:=]?\s*(\d+\.?\d*)",
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[key] = float(match.group(1))
        
        return extracted