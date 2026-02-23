class AcidBaseAnalyzer:
    def analyze(self, ph, pco2, hco3, na=140.0, cl=104.0):
        results = {"status": "Normal", "primary": "", "compensation": "", "delta_delta": ""}
        
        if ph < 7.35:
            results["status"] = "Acidemia"
            
            if hco3 < 22:
                results["primary"] = "Acidose Metabólica"
                
                # Fórmula de Winter
                pco2_esperada = (1.5 * hco3) + 8
                results["compensation"] = f"pCO2 Esperada (Winter): {pco2_esperada:.1f} ± 2 mmHg"
                
                # Ânion Gap
                ag = na - (cl + hco3)
                results["primary"] += f" (Anion Gap: {ag:.1f})"
                
                # Relação Delta/Delta
                if ag > 12:
                    delta_ag = ag - 12
                    delta_hco3 = 24 - hco3
                    ratio = delta_ag / delta_hco3 if delta_hco3 != 0 else 0
                    
                    if ratio < 0.4:
                        results["delta_delta"] = f"Δ/Δ = {ratio:.2f} (Acidose Hiperclorêmica associada)"
                    elif 0.4 <= ratio <= 0.8:
                        results["delta_delta"] = f"Δ/Δ = {ratio:.2f} (Distúrbio Misto: AG normal e elevado)"
                    elif 1.0 <= ratio <= 2.0:
                        results["delta_delta"] = f"Δ/Δ = {ratio:.2f} (Acidose Metabólica de AG elevado pura)"
                    else:
                        results["delta_delta"] = f"Δ/Δ = {ratio:.2f} (Alcalose Metabólica associada)"

            elif pco2 > 45:
                results["primary"] = "Acidose Respiratória"

        elif ph > 7.45:
            results["status"] = "Alcalemia"
            if hco3 > 26:
                results["primary"] = "Alcalose Metabólica"
            elif pco2 < 35:
                results["primary"] = "Alcalose Respiratória"
                
        return results