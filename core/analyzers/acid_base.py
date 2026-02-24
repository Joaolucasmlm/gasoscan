class AcidBaseAnalyzer:
    def analyze(self, ph, pco2, hco3, na=140.0, cl=104.0):
        results = {"status": "", "primary": "", "conclusion": "", "disturbios": []}
        
        # 1. Status do pH
        if ph < 7.35: 
            results["status"] = "Acidemia"
        elif ph > 7.45: 
            results["status"] = "Alcalemia"
        else: 
            if (not 35 <= pco2 <= 45) or (not 22 <= hco3 <= 26):
                results["status"] = "pH Normal (Distúrbio Misto)"
            else:
                results["status"] = "Normal"
                results["primary"] = "Nenhum distúrbio"
                results["conclusion"] = "✅ Exame dentro dos padrões de normalidade"
                return results
                
        disturbios = []
        delta_pco2 = abs(pco2 - 40)
        
        # 2. Ânion Gap e Delta/Delta
        ag = na - (cl + hco3)
        tem_ac_metabolica = False
        tem_alc_metabolica = False

        if ag > 12:
            disturbios.append(f"Acidose Metabólica AG Elevado ({ag:.1f})")
            tem_ac_metabolica = True
            
            delta_ag = ag - 12
            delta_hco3_met = 24 - hco3
            ratio = delta_ag / delta_hco3_met if delta_hco3_met != 0 else 0
            
            if ratio < 0.4: 
                disturbios.append("Acidose Metabólica Hiperclorêmica Associada")
            elif ratio > 2.0: 
                disturbios.append("Alcalose Metabólica Associada")
                tem_alc_metabolica = True

        # 3. Acidose Metabólica de AG Normal
        if hco3 < 22 and ag <= 12:
            disturbios.append("Acidose Metabólica AG Normal (Hiperclorêmica)")
            tem_ac_metabolica = True
            
        # 4. Alcalose Metabólica
        if hco3 > 26 and not tem_alc_metabolica:
            disturbios.append("Alcalose Metabólica")
            tem_alc_metabolica = True

        # 5. Distúrbios Respiratórios (Agudo vs Crônico)
        if pco2 > 45:
            hco3_esp_agudo = 24 + (delta_pco2 / 10) * 1
            hco3_esp_cronico = 24 + (delta_pco2 / 10) * 3.5
            if abs(hco3 - hco3_esp_agudo) < abs(hco3 - hco3_esp_cronico):
                disturbios.append("Acidose Respiratória AGUDA")
            else:
                disturbios.append("Acidose Respiratória CRÔNICA")
                
        elif pco2 < 35:
            hco3_esp_agudo = 24 - (delta_pco2 / 10) * 2
            hco3_esp_cronico = 24 - (delta_pco2 / 10) * 5
            if abs(hco3 - hco3_esp_agudo) < abs(hco3 - hco3_esp_cronico):
                disturbios.append("Alcalose Respiratória AGUDA")
            else:
                disturbios.append("Alcalose Respiratória CRÔNICA")

        # 6. Avaliação de Compensação (Foco no distúrbio primário pelo pH)
        conclusao = []
        
        if tem_ac_metabolica and ph <= 7.40:
            pco2_esp = (1.5 * hco3) + 8
            if pco2 > (pco2_esp + 2):
                conclusao.append(f"❌ NÃO COMPENSADO: Acidose Respiratória Associada (pCO2 real {pco2} > esperada {pco2_esp+2:.1f})")
            elif pco2 < (pco2_esp - 2):
                conclusao.append(f"❌ NÃO COMPENSADO: Alcalose Respiratória Associada (pCO2 real {pco2} < esperada {pco2_esp-2:.1f})")
            else:
                conclusao.append(f"✅ COMPENSADO: Resposta respiratória adequada à Acidose (pCO2 esp. {pco2_esp:.1f} ± 2)")
                
        elif tem_alc_metabolica and ph > 7.40:
            pco2_esp = 40 + 0.7 * (hco3 - 24)
            if pco2 < (pco2_esp - 2):
                conclusao.append(f"❌ NÃO COMPENSADO: Alcalose Respiratória Associada (pCO2 real {pco2} < esperada {pco2_esp-2:.1f})")
            elif pco2 > (pco2_esp + 2):
                conclusao.append(f"❌ NÃO COMPENSADO: Acidose Respiratória Associada (pCO2 real {pco2} > esperada {pco2_esp+2:.1f})")
            else:
                conclusao.append(f"✅ COMPENSADO: Resposta respiratória adequada à Alcalose (pCO2 esp. {pco2_esp:.1f} ± 2)")
        
        elif not tem_ac_metabolica and not tem_alc_metabolica:
             conclusao.append("🔄 Distúrbio primário respiratório. Verifique a cronicidade (agudo/crônico) nos achados acima.")

        results["primary"] = " | ".join(disturbios) if disturbios else "Sem distúrbios óbvios"
        results["conclusion"] = "\n".join(conclusao)
        
        return results
