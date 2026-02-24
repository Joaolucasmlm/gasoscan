class AcidBaseAnalyzer:
    def analyze(self, ph, pco2, hco3, na=140.0, cl=104.0):
        results = {"status": "", "primary": "", "conclusion": "", "disturbios": []}
        
        # 1. Status do pH
        if ph < 7.35: results["status"] = "Acidemia"
        elif ph > 7.45: results["status"] = "Alcalemia"
        else: results["status"] = "pH Normal (Possível Distúrbio Misto)"
                
        disturbios = []
        
        # 2. Ânion Gap (Sempre calculado)
        ag = na - (cl + hco3)
        if ag > 12:
            disturbios.append(f"Acidose Metabólica AG Elevado ({ag:.1f})")
            
            # 3. Delta/Delta (Análise Interna)
            delta_ag = ag - 12
            delta_hco3 = 24 - hco3
            ratio = delta_ag / delta_hco3 if delta_hco3 != 0 else 0
            
            if ratio < 0.4: disturbios.append("Acidose Metabólica Hiperclorêmica Associada")
            elif ratio > 2.0: disturbios.append("Alcalose Metabólica Associada")

        # 4. Acidose Metabólica de AG Normal
        if hco3 < 22 and ag <= 12:
            disturbios.append("Acidose Metabólica AG Normal (Hiperclorêmica)")
            
        # 5. Avaliação da Compensação (A sua solicitação)
        compensacao_str = ""
        if "Acidose Metabólica" in " ".join(disturbios):
            pco2_esperada = (1.5 * hco3) + 8
            margem = 2
            
            if pco2 > (pco2_esperada + margem):
                compensacao_str = f"❌ NÃO COMPENSADO: Acidose Respiratória Associada (pCO2 real {pco2} > esperada {pco2_esperada + margem})"
            elif pco2 < (pco2_esperada - margem):
                compensacao_str = f"❌ NÃO COMPENSADO: Alcalose Respiratória Associada (pCO2 real {pco2} < esperada {pco2_esperada - margem})"
            else:
                compensacao_str = f"✅ COMPENSADO: Resposta respiratória adequada (pCO2 esperada: {pco2_esperada:.1f} ± 2)"

        # 6. Distúrbios Respiratórios Primários
        if pco2 > 45 and "Acidose Metabólica" not in " ".join(disturbios):
            disturbios.append("Acidose Respiratória")
        elif pco2 < 35 and "Acidose Metabólica" not in " ".join(disturbios):
            disturbios.append("Alcalose Respiratória")

        # 7. Alcalose Metabólica Primária
        if hco3 > 26 and "Alcalose Metabólica" not in " ".join(disturbios):
            disturbios.append("Alcalose Metabólica")

        results["primary"] = " | ".join(disturbios) if disturbios else "Sem distúrbios óbvios"
        results["conclusion"] = compensacao_str
        
        return results
