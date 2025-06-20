# Constantes para o projeto FII AI

# Lista de FIIs por tipo
# Em uma aplicação real, essas listas seriam obtidas através de consultas a APIs ou scrapers
FII_TYPES = {
    # Fundos de CRI
    "cri": [
        "KNCR11", "KNIP11", "KNHY11", "HGCR11", "VGIR11", 
        "RECR11", "IRDM11", "RBRY11", "VCJR11", "KCRE11",
        "KNSC11", "KNUQ11", "KFEN11", "RCRB11", "BTCR11",
        "VCRR11", "MCCI11", "VRTA11", "RZTR11", "OUFF11"
    ],
    
    # Fundos de Shopping
    "shopping": [
        "VISC11", "XPML11", "MALL11", "HGBS11", "HSML11", 
        "VRTA11", "SHOP11", "SHUL11", "ATSA11", "FIGS11",
        "BPML11", "PQDP11", "HPDP11", "VSHO11", "FLRP11",
        "ABCP11", "SHPH11", "SPVJ11", "FVPQ11", "JRDM11",
        "ELDO11", "SHDP11", "SCPF11", "WPLZ11", "VPSI11"
    ],
    
    # Fundos de Logística
    "logistica": [
        "VILG11", "HGLG11", "BRCO11", "BTLG11", "LVBI11", 
        "XPLG11", "CXTL11", "SDIL11", "OULG11", "LGCP11",
        "DERE11", "ALZR11", "PLOG11", "PATL11", "HSLG11",
        "VSLG11", "GALG11", "RBRL11", "VTLT11", "GGRD11"
    ],
    
    # Fundos de Escritório
    "escritorio": [
        "BRCR11", "HGRE11", "RBRP11", "PVBI11", "JSRE11", 
        "KNRI11", "RCRB11", "GTWR11", "ALMI11", "EDGA11",
        "BBPO11", "VINO11", "RBED11", "THRA11", "HGPO11",
        "TEPP11", "ONEF11", "BTRA11", "FIIB11"
    ],
    
    # Fundos de Renda Urbana
    "renda_urbana": [
        "KNSC11", "HCTR11", "TRXF11", "GGRC11", "VINO11", 
        "BBPO11", "RBVA11", "HCST11", "LASC11", "MGCR11",
        "XPPR11", "RZAK11", "RBRS11", "HOSI11", "GSFI11",
        "BARI11", "HFOF11", "MFII11", "XPSF11", "VGIR11"
    ],
    
    # Fundos de Fundos (FoF)
    "fof": [
        "RBFF11", "KFOF11", "HFOF11", "BCIA11", "HABT11", 
        "CFHI11", "XPFT11", "BCFF11", "IFIE11", "ARRI11",
        "QIFF11", "RFOF11", "HFOF11", "IBFF11", "FOFT11",
        "AFHI11", "BPFF11", "IRDM11", "KFOF11", "MGFF11"
    ]
}

# Mapeamento de tipos de FII para nomes amigáveis em português
FII_TYPE_NAMES = {
    "cri": "Fundos de CRI",
    "shopping": "Fundos de Shopping",
    "logistica": "Fundos de Logística",
    "escritorio": "Fundos de Escritório",
    "renda_urbana": "Fundos de Renda Urbana",
    "fof": "Fundos de Fundos (FoF)"
}

# Alocação recomendada por tipo de FII
RECOMMENDED_ALLOCATION = {
    "cri": 0.27,  # 27% em Fundos CRI
    "shopping": 0.17,  # 17% em Fundos de Shopping
    "logistica": 0.17,  # 17% em Fundos de Logística
    "escritorio": 0.16,  # 16% em Fundos de Escritório
    "renda_urbana": 0.09,  # 9% em Renda Urbana
    "fof": 0.14  # 14% em FoF
}

# Informações de dividend yield mensal por FII
# Obs: Em um ambiente real, esses dados seriam obtidos via API ou scraping
# Os valores abaixo são estimativas para fins de demonstração
FII_DIVIDEND_INFO = {
    # CRI
    "KNCR11": {"dividend_yield": 0.0090, "last_dividend": 0.95, "price": 105.38},
    "KNIP11": {"dividend_yield": 0.0098, "last_dividend": 1.03, "price": 104.90},
    "KNHY11": {"dividend_yield": 0.0115, "last_dividend": 1.21, "price": 105.22},
    "HGCR11": {"dividend_yield": 0.0092, "last_dividend": 1.12, "price": 121.74},
    "VGIR11": {"dividend_yield": 0.0088, "last_dividend": 0.92, "price": 104.54},
    "RECR11": {"dividend_yield": 0.0105, "last_dividend": 1.25, "price": 119.05},
    "IRDM11": {"dividend_yield": 0.0112, "last_dividend": 1.21, "price": 108.04},
    "RBRY11": {"dividend_yield": 0.0097, "last_dividend": 0.95, "price": 97.94},
    "VCJR11": {"dividend_yield": 0.0095, "last_dividend": 0.93, "price": 97.89},
    "KCRE11": {"dividend_yield": 0.0086, "last_dividend": 0.85, "price": 98.83},
    "KNSC11": {"dividend_yield": 0.0094, "last_dividend": 0.96, "price": 102.13},
    "KNUQ11": {"dividend_yield": 0.0092, "last_dividend": 0.85, "price": 92.39},
    "KFEN11": {"dividend_yield": 0.0106, "last_dividend": 1.10, "price": 103.77},
    "RCRB11": {"dividend_yield": 0.0089, "last_dividend": 0.93, "price": 104.49},
    "BTCR11": {"dividend_yield": 0.0103, "last_dividend": 1.05, "price": 101.94},
    "VCRR11": {"dividend_yield": 0.0099, "last_dividend": 0.98, "price": 98.99},
    "MCCI11": {"dividend_yield": 0.0095, "last_dividend": 0.96, "price": 101.05},
    "VRTA11": {"dividend_yield": 0.0093, "last_dividend": 0.89, "price": 95.70},
    "RZTR11": {"dividend_yield": 0.0110, "last_dividend": 1.08, "price": 98.18},
    "OUFF11": {"dividend_yield": 0.0088, "last_dividend": 0.87, "price": 98.86},
    
    # Shopping
    "VISC11": {"dividend_yield": 0.0080, "last_dividend": 0.70, "price": 87.50},
    "XPML11": {"dividend_yield": 0.0075, "last_dividend": 0.65, "price": 86.67},
    "MALL11": {"dividend_yield": 0.0066, "last_dividend": 0.56, "price": 84.85},
    "HGBS11": {"dividend_yield": 0.0078, "last_dividend": 0.72, "price": 92.31},
    "HSML11": {"dividend_yield": 0.0070, "last_dividend": 0.60, "price": 85.71},
    
    # Logística
    "VILG11": {"dividend_yield": 0.0082, "last_dividend": 0.90, "price": 109.76},
    "HGLG11": {"dividend_yield": 0.0073, "last_dividend": 0.98, "price": 134.24},
    "BRCO11": {"dividend_yield": 0.0085, "last_dividend": 0.83, "price": 97.65},
    "BTLG11": {"dividend_yield": 0.0075, "last_dividend": 0.75, "price": 100.00},
    "LVBI11": {"dividend_yield": 0.0087, "last_dividend": 0.88, "price": 101.15},
    
    # Escritório
    "BRCR11": {"dividend_yield": 0.0068, "last_dividend": 0.50, "price": 73.53},
    "HGRE11": {"dividend_yield": 0.0063, "last_dividend": 0.58, "price": 92.06},
    "RBRP11": {"dividend_yield": 0.0072, "last_dividend": 0.60, "price": 83.33},
    "PVBI11": {"dividend_yield": 0.0070, "last_dividend": 0.55, "price": 78.57},
    "JSRE11": {"dividend_yield": 0.0065, "last_dividend": 0.48, "price": 73.85},
    
    # Renda Urbana
    "TRXF11": {"dividend_yield": 0.0083, "last_dividend": 0.82, "price": 98.80},
    "GGRC11": {"dividend_yield": 0.0085, "last_dividend": 0.85, "price": 100.00},
    "HCTR11": {"dividend_yield": 0.0080, "last_dividend": 0.78, "price": 97.50},
    "RBVA11": {"dividend_yield": 0.0082, "last_dividend": 0.75, "price": 91.46},
    "HCST11": {"dividend_yield": 0.0078, "last_dividend": 0.72, "price": 92.31},
    
    # FOF
    "RBFF11": {"dividend_yield": 0.0076, "last_dividend": 0.62, "price": 81.58},
    "KFOF11": {"dividend_yield": 0.0079, "last_dividend": 0.68, "price": 86.08},
    "HFOF11": {"dividend_yield": 0.0082, "last_dividend": 0.70, "price": 85.37},
    "BCIA11": {"dividend_yield": 0.0075, "last_dividend": 0.65, "price": 86.67},
    "HABT11": {"dividend_yield": 0.0080, "last_dividend": 0.68, "price": 85.00}
} 