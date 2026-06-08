import math

VALORES_TIPICOS = {
    "Alisol":   {"ph": 6.6, "co": 0.86, "k": 0.26, "p": 0.09,  "ca": 3.2,  "mg": 2.38},
    "Cambisol": {"ph": 7.3, "co": 1.43, "k": 5.15, "p": 33.3,  "ca": 16.6, "mg": 2.40},
    "Phaeozem": {"ph": 7.0, "co": 1.11, "k": 0.18, "p": 5.60,  "ca": 11.8, "mg": 3.81},
    "Vertisol": {"ph": 7.2, "co": 2.30, "k": 0.45, "p": 12.0,  "ca": 14.5, "mg": 3.20},
    "Regosol":  {"ph": 6.0, "co": 0.48, "k": 0.82, "p": 4.12,  "ca": 4.93, "mg": 0.86},
    "Luvisol":  {"ph": 6.1, "co": 0.62, "k": 0.42, "p": 1.62,  "ca": 5.34, "mg": 1.16},
    "Fluvisol": {"ph": 6.8, "co": 0.18, "k": 1.38, "p": 3.63,  "ca": 3.23, "mg": 0.73},
    "Umbrisol": {"ph": 6.4, "co": 1.50, "k": 1.36, "p": 1.91,  "ca": 3.17, "mg": 0.81},
}

TIPOS_SUELO_DESC = {
    "Alisol":   "Arcilloso-rojizo",
    "Cambisol": "Fertil, buen drenaje",
    "Phaeozem": "Oscuro, rico en nutrientes",
    "Vertisol": "Arcilla negra",
    "Regosol":  "Suelo joven, arenoso",
    "Luvisol":  "Con acumulacion de arcilla",
    "Fluvisol": "Suelo de vega",
    "Umbrisol": "Acido, boscoso",
}

def calcular_indice(datos: dict) -> float:
   
    score = 0.0

    if 6 <= datos["ph"] <= 7:
        score += 2
    elif datos["ph"] >= 5.5:
        score += 1

    score += min(datos["co"] / 1.5, 1) * 2

    score += min(datos["k"] / 0.30, 1) * 1.5

    score += min(datos["p"] / 5.0, 1) * 1.5

    score += min(datos["ca"] / 5.0, 1) * 1

    score += min(datos["mg"] / 0.50, 1) * 1

    sb = ((datos["ca"] + datos["mg"] + datos["k"]) / 20) * 100
    if sb >= 50:
        score += 1

    return round(min(10.0, score), 1)

    
def calcular_recomendacion(datos: dict) -> dict:
   
    n_disponible = datos["co"] * 3.6
    n_requerido  = 90
    n_fert = max(0, n_requerido - n_disponible - 30)
    p_fert = max(0, 40 - datos["p"] * 0.4)
    k_fert = max(0, 60 - datos["k"] * 47)

    return {
        "n": round(n_fert),
        "p": round(p_fert),
        "k": round(k_fert),
    }


def estimar_rendimiento(indice: float) -> float:
   
    return round(2.2 + indice / 6, 1)


def calcular_costo_fertilizantes(necesidades: dict) -> int:
    
    return round(necesidades["n"] * 26 + necesidades["p"] * 38 + necesidades["k"] * 24)


def suelo_inteligente_miaf(
    agricultor: str,
    localidad: str,
    area: float,
    tipo_suelo: str,
    ph: float = None,
    co: float = None,
    k: float = None,
    p: float = None,
    ca: float = None,
    mg: float = None,
) -> dict:
   
    if tipo_suelo not in VALORES_TIPICOS:
        raise ValueError(f"Tipo de suelo no reconocido: '{tipo_suelo}'. "
                         f"Opciones: {list(VALORES_TIPICOS.keys())}")

    defaults = VALORES_TIPICOS[tipo_suelo]
    datos = {
        "ph": ph  if ph  is not None else defaults["ph"],
        "co": co  if co  is not None else defaults["co"],
        "k":  k   if k   is not None else defaults["k"],
        "p":  p   if p   is not None else defaults["p"],
        "ca": ca  if ca  is not None else defaults["ca"],
        "mg": mg  if mg  is not None else defaults["mg"],
    }

    indice       = calcular_indice(datos)
    necesidades  = calcular_recomendacion(datos)
    rendimiento  = estimar_rendimiento(indice)
    costo        = calcular_costo_fertilizantes(necesidades)

    if indice >= 7:
        nivel = "ALTA"
    elif indice >= 4.5:
        nivel = "MEDIA"
    else:
        nivel = "BAJA - MEJORABLE"

    if datos["ph"] < 5.8:
        alerta_ph = f"pH acido ({datos['ph']}). Aplicar cal agricola 500-800 kg/ha un mes antes de sembrar."
    elif datos["ph"] > 7.3:
        alerta_ph = f"pH alcalino ({datos['ph']}). Usar sulfato de amonio o azufre elemental."
    else:
        alerta_ph = f"pH optimo ({datos['ph']}) para maiz, frijol y arboles frutales."

    return {
        "agricultor":  agricultor,
        "localidad":   localidad,
        "area_ha":     area,
        "tipo_suelo":  tipo_suelo,
        "descripcion": TIPOS_SUELO_DESC[tipo_suelo],
        "datos":       datos,
        "indice_fertilidad": indice,
        "nivel_fertilidad":  nivel,
        "necesidades_kg_ha": necesidades,
        "costo_fertilizante_mxn_ha": costo,
        "costo_total_mxn": round(costo * area),
        "rendimiento_estimado_ton_ha": rendimiento,
        "alerta_ph": alerta_ph,
    }

def suelo_inteligente_miaf(resultado: dict) -> None:
   
    print("  SUELO INTELIGENTE - Asistente MIAF")
    print("  Milpa Intercalada con Arboles Frutales | Oaxaca")
    
    print(f"  Agricultor : {resultado['agricultor']}")
    print(f"  Localidad  : {resultado['localidad']}")
    print(f"  Area       : {resultado['area_ha']} hectareas")
    print(f"  Tipo suelo : {resultado['tipo_suelo']} ({resultado['descripcion']})")
    print()

    print(" PARAMETROS ANALIZADOS ")
    d = resultado["datos"]
    print(f"  pH              : {d['ph']}")
    print(f"  Carbono organico: {d['co']} %")
    print(f"  Potasio         : {d['k']} cmol/kg")
    print(f"  Fosforo         : {d['p']} mg/kg")
    print(f"  Calcio          : {d['ca']} cmol/kg")
    print(f"  Magnesio        : {d['mg']} cmol/kg")
    print()

    indice = resultado["indice_fertilidad"]
    nivel  = resultado["nivel_fertilidad"]

    print(f"  INDICE DE FERTILIDAD: {indice} / 10")
    print(f"  NIVEL: {nivel}")
    print()

    print("  --- RECOMENDACION DE FERTILIZACION ---")
    nec = resultado["necesidades_kg_ha"]
    if nec["n"] > 0 or nec["p"] > 0 or nec["k"] > 0:
        print(f"  Nitrogeno (N) : {nec['n']} kg/ha")
        print(f"  Fosforo   (P) : {nec['p']} kg/ha")
        print(f"  Potasio   (K) : {nec['k']} kg/ha")
        print(f"  Costo estimado: ${resultado['costo_fertilizante_mxn_ha']} MXN/ha")
        print(f"  Costo total   : ${resultado['costo_total_mxn']} MXN ({resultado['area_ha']} ha)")
        print("  Aplicar en 2 momentos: siembra y 30-40 dias despues.")
    else:
        print("  Suelo equilibrado. Solo mantenimiento con abonos organicos.")

    print()
    print(f"  ALERTA pH: {resultado['alerta_ph']}")
    print()
    print(f"  RENDIMIENTO ESTIMADO: {resultado['rendimiento_estimado_ton_ha']} ton/ha")
    print("  (maiz + frijol + calabaza en sistema MIAF)")

def solicitar_float(mensaje: str, default: float = None) -> float:

    while True:
        entrada = input(mensaje).strip()
        if entrada == "" and default is not None:
            return default
        try:
            return float(entrada)
        except ValueError:
            print("  [!] Ingrese un numero valido o presione Enter para usar el valor tipico.")


def menu_tipo_suelo() -> str:
    
    tipos = list(VALORES_TIPICOS.keys())
    print("\n  Tipos de suelo disponibles:")
    for i, t in enumerate(tipos, 1):
        print(f"    {i}. {t} - {TIPOS_SUELO_DESC[t]}")
    while True:
        entrada = input("  Seleccione numero (1-8) [default: 2 Cambisol]: ").strip()
        if entrada == "":
            return "Cambisol"
        try:
            idx = int(entrada) - 1
            if 0 <= idx < len(tipos):
                return tipos[idx]
        except ValueError:
            pass
        print("  [!] Opcion no valida. Intente de nuevo.")


def modo_interactivo():
    
    print("  SUELO INTELIGENTE - Asistente MIAF")
    print("  Ingrese los datos de su parcela")

    agricultor = input("  Nombre del agricultor: ").strip() or "Agricultor"
    localidad  = input("  Localidad/Municipio (Oaxaca): ").strip() or "Oaxaca"
    area       = solicitar_float("  Area en hectareas [default: 1.5]: ", 1.5)
    tipo_suelo = menu_tipo_suelo()

    defaults = VALORES_TIPICOS[tipo_suelo]
    print(f"\n  Ingrese datos del analisis de suelo.")
    print(f"  (Presione Enter para usar valor tipico de {tipo_suelo})\n")

    ph = solicitar_float(f"  pH [tipico: {defaults['ph']}]: ", defaults["ph"])
    co = solicitar_float(f"  Carbono organico % [tipico: {defaults['co']}]: ", defaults["co"])
    k  = solicitar_float(f"  Potasio cmol/kg [tipico: {defaults['k']}]: ", defaults["k"])
    p  = solicitar_float(f"  Fosforo mg/kg [tipico: {defaults['p']}]: ", defaults["p"])
    ca = solicitar_float(f"  Calcio cmol/kg [tipico: {defaults['ca']}]: ", defaults["ca"])
    mg = solicitar_float(f"  Magnesio cmol/kg [tipico: {defaults['mg']}]: ", defaults["mg"])

    resultado = suelo_inteligente_miaf.analizar_suelo(
        agricultor, localidad, area, tipo_suelo,
        ph=ph, co=co, k=k, p=p, ca=ca, mg=mg
    )
    print()
    suelo_inteligente_miaf.imprimir_reporte(resultado)


def ejemplo_uso():
    print("\n--- Ejemplo de uso programatico ---\n")

    resultado = suelo_inteligente_miaf.analizar_suelo(
        agricultor="Maria Lopez",
        localidad="Valles Centrales",
        area=2.0,
        tipo_suelo="Cambisol",
        ph=6.4,
        co=1.2,
        k=0.35,
        p=8.5,
        ca=5.2,
        mg=0.9,
    )
    suelo_inteligente_miaf.imprimir_reporte(resultado)

    # Acceder a valores individuales
    print(f"\nIndice: {resultado['indice_fertilidad']}")
    print(f"Nivel : {resultado['nivel_fertilidad']}")
    print(f"N recomendado: {resultado['necesidades_kg_ha']['n']} kg/ha")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--ejemplo":
        ejemplo_uso()
    else:
        modo_interactivo()
