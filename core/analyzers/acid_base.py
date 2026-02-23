from domain.models import BloodGasData

class AcidBaseAnalyzer:
    def __init__(self, data: BloodGasData):
        self.data = data
        self.disorders = []
        self.notes = []

    def analyze(self):
        self._check_primary()
        self._check_respiratory_chronicity()
        
        if self.data.has_ionogram:
            self._evaluate_metabolic_complexities()
            
        return {"disorders": self.disorders, "notes": self.notes}

    def _check_primary(self):
        """Avaliação inicial de Acidemia/Alcalemia."""
        # Faixas de referência: pH 7.35-7.45 | pCO2 35-45 | HCO3 22-26
        if self.data.ph < 7.35:
            if self.data.hco3 < 22: self.disorders.append("Acidose Metabólica")
            if self.data.pco2 > 45: self.disorders.append("Acidose Respiratória")
        elif self.data.ph > 7.45:
            if self.data.hco3 > 26: self.disorders.append("Alcalose Metabólica")
            if self.data.pco2 < 35: self.disorders.append("Alcalose Respiratória")
        else: # pH Normal
            if self.data.hco3 < 22 and self.data.pco2 < 35:
                self.disorders.extend(["Acidose Metabólica", "Alcalose Respiratória"])
            elif self.data.hco3 > 26 and self.data.pco2 > 45:
                self.disorders.extend(["Alcalose Metabólica", "Acidose Respiratória"])
            elif not self.disorders:
                self.disorders.append("Gasometria Normal ou Basal")

    def _check_respiratory_chronicity(self):
        """Diferenciação Agudo vs Crônico."""
        delta_pco2 = abs(self.data.pco2 - 40)
        
        if "Acidose Respiratória" in self.disorders:
            # +1 mEq de BIC para cada 10 de pCO2 (Agudo) | +4 mEq (Crônico)
            exp_agudo = 24 + (0.1 * delta_pco2)
            exp_cronico = 24 + (0.4 * delta_pco2)
            self._label_respiratory(exp_agudo, exp_cronico, "Acidose")
            
        elif "Alcalose Respiratória" in self.disorders:
            # -2 mEq de BIC para cada 10 de pCO2 (Agudo) | -4 a 5 mEq (Crônico)
            exp_agudo = 24 - (0.2 * delta_pco2)
            exp_cronico = 24 - (0.4 * delta_pco2)
            self._label_respiratory(exp_agudo, exp_cronico, "Alcalose")

    def _label_respiratory(self, agudo, cronico, tipo):
        if abs(self.data.hco3 - agudo) < 1.5: status = "Aguda"
        elif abs(self.data.hco3 - cronico) < 2.0: status = "Crônica"
        else: status = "Crônica Agudizada"
        self.disorders = [d.replace(f"{tipo} Respiratória", f"{tipo} Respiratória {status}") for d in self.disorders]

    def _evaluate_metabolic_complexities(self):
        """Cálculo de Anion Gap e Delta/Delta."""
        ag = self.data.na - (self.data.cl + self.data.hco3)
        # AG corrigido pela Albumina: AG + 2.5 * (4.5 - Alb)
        ag_corr = ag + 2.5 * (4.5 - self.data.albumina)
        
        if ag_corr > 12:
            self.notes.append(f"Anion Gap Elevado: {ag_corr:.1f} mEq/L")
            if "Acidose Metabólica" in self.disorders:
                delta_ag = ag_corr - 12
                delta_hco3 = 24 - self.data.hco3
                ratio = delta_ag / delta_hco3 if delta_hco3 != 0 else 0
                
                # Interpretação Delta/Delta
                if ratio < 1:
                    self.disorders.append("Acidose Metabólica Hiperclorêmica Associada")
                elif ratio > 2:
                    self.disorders.append("Alcalose Metabólica Associada")