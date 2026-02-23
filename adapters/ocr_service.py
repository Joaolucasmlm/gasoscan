import easyocr
import re
import numpy as np
from PIL import Image

class GasoOCR:
    def __init__(self):
        # Otimizado: Sem GPU e apenas um idioma para economizar RAM
        self.reader = easyocr.Reader(['pt'], gpu=False)
        
    def scan_image(self, image_bytes):
        img = Image.open(image_bytes)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensiona para evitar estouro de memória
        img.thumbnail((1000, 1000)) 
        img_np = np.array(img)
        
        result = self.reader.readtext(img_np, detail=0)
        full_text = " ".join(result).replace(",", ".") 
        return self._parse_values(full_text)

    def _parse_values(self, text):
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