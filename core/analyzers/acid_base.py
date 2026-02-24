class AcidBaseAnalyzer:
    def analyze(self, ph, pco2, hco3, na=140.0, cl=104.0):
        results = {
            "status": "", 
            "primary": "", 
            "compensation": "", 
            "delta_delta": ""
        }
        
        # 1. Status do pH
        if ph < 7.35:
            results["status"] = "Acidemia"
        elif ph > 7.45:
            results["status"] = "Alcalemia"
        else:
            # Checa se o pH está normal, mas esconde um distúrbio misto
            if not (35 <= pco2 <= 45) or not (22 <= hco3 <= 26):
                results["status"] = "pH Normal (Distúrbio Misto)"
            else:
                results["status"] = "Normal"
                return results # Se tudo está normal, para aqui.
                
        disturbios = []
        
        # 2. Ânion Gap (Calculado SEMPRE)
        ag = na - (cl + hco3)
        if ag > 12:
            disturbios.append(f"Acidose Metabólica com AG Elevado ({ag:.1f})")
            
            # 3. Relação Delta/Delta
            delta_ag = ag - 12
            delta_hco3 = 24 - hco3
            if delta_hco3 == 0: delta_hco3 = 0.1 # Evita erro de divisão por zero
            ratio = delta_ag / delta_hco3
            
            results["delta_delta"] = f"Razão Δ/Δ: {ratio:.2f}"
            
            if ratio < 0.4:
                disturbios.append("Acidose Metabólica Hiperclorêmica")
            elif ratio > 2.0:
                disturbios.append("Alcalose Metabólica")

        # 4. Avaliação Direcional de HCO3 e pCO2
        # Acidose Metabólica com AG Normal (Hiperclorêmica)
        if hco3 < 22 and ag <= 12:
            disturbios.append("Acidose Metabólica (AG Normal)")
            
        # Alcalose Metabólica
        if hco3 > 26 and "Alcalose Metabólica" not in " ".join(disturbios):
            disturbios.append("Alcalose Metabólica")
            
        # Acidose Respiratória
        if pco2 > 45:
            disturbios.append("Acidose Respiratória")
            
        # Alcalose Respiratória
        if pco2 < 35:
            disturbios.append("Alcalose Respiratória")

        # 5. Avaliação de Compensação (Fórmula de Winter)
        if "Acidose Metabólica" in " ".join(disturbios):
            pco2_esperada = (1.5 * hco3) + 8
            limite_inf = pco2_esperada - 2
            limite_sup = pco2_esperada + 2
            
            results["compensation"] = f"Compensação: pCO2 esperada entre {limite_inf:.1f} e {limite_sup:.1f} mmHg"
            
            # Checa falha na compensação respiratória
            if pco2 > limite_sup and "Acidose Respiratória" not in disturbios:
                disturbios.append("Acidose Respiratória (Falha de Compensação)")
            elif pco2 < limite_inf and "Alcalose Respiratória" not in disturbios:
                disturbios.append("Alcalose Respiratória (Hiperventilação excessiva)")

        # Formata o diagnóstico final unindo todos os distúrbios encontrados
        results["primary"] = " | ".join(disturbios)
        
        return results
