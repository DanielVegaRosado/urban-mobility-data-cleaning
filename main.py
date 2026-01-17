import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración general de estilo
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# PARTE 1: GENERACIÓN DEL DATASET
print("--- 1. Generando datos simulados ---")
np.random.seed(42) # Semilla para reproducibilidad
n_registros = 200

fechas = pd.date_range(start="2025-01-01", periods=n_registros, freq="D")
medios_transporte = ["autobus", "metro", "bicicleta", "coche", "a_pie"]
zonas = ["centro", "norte", "sur", "este", "oeste"]
usuarios = ["U01", "U02", "U03", "U04", "U05", "U06", "U07", "U08"]

datos = {
    "fecha": np.random.choice(fechas, n_registros),
    "medio_transporte": np.random.choice(medios_transporte, n_registros),
    "distancia_km": np.round(np.random.uniform(1, 50, n_registros), 2),
    "duracion_min": np.random.randint(1, 100, n_registros),
    "zona": np.random.choice(zonas, n_registros),
    "usuario": np.random.choice(usuarios, n_registros)
}

df = pd.DataFrame(datos)
df.to_csv("movilidad_urbana1.csv", index=False)

# PARTE 2: INTRODUCCIÓN DE VALORES NULOS
print("--- 2. Introduciendo valores nulos ---")
np.random.seed(123)
df = pd.read_csv("movilidad_urbana1.csv")

# Introducir nulos en el 10% de 'duracion_min' y 'usuario'
df.loc[df.sample(frac=0.1).index, 'duracion_min'] = np.nan
df.loc[df.sample(frac=0.1).index, 'usuario'] = np.nan

# Guardamos el estado sucio de nulos
df.to_csv("movilidad_urbana2.csv", index=False)

# PARTE 3: LIMPIEZA DE VALORES NULOS
print("--- 3. Limpiando valores nulos ---")
# Imputación numérica (Mediana)
df['duracion_min'] = df['duracion_min'].fillna(df['duracion_min'].median())

# Imputación categórica (Moda)
moda_usuario = df['usuario'].mode()[0]
df['usuario'] = df['usuario'].fillna(moda_usuario)

# Guardamos el estado limpio de nulos
df.to_csv("movilidad_urbana3.csv", index=False)

# PARTE 4: INTRODUCCIÓN Y DETECCIÓN DE OUTLIERS
print("--- 4. Gestionando Outliers ---")
# Introducir outliers: Multiplicamos por 10 el 5% de las distancias
indices_outliers = df.sample(frac=0.05).index
df.loc[indices_outliers, 'distancia_km'] = df['distancia_km'] * 10
df.to_csv("movilidad_urbana4.csv", index=False) # Estado sucio de outliers

# Detección IQR (Rango Intercuartílico)
Q1_dist = df['distancia_km'].quantile(0.25)
Q3_dist = df['distancia_km'].quantile(0.75)
IQR_dist = Q3_dist - Q1_dist
limite_inf = Q1_dist - 1.5 * IQR_dist
limite_sup = Q3_dist + 1.5 * IQR_dist

print(f"Límites IQR detectados: Inferior={limite_inf:.2f}, Superior={limite_sup:.2f}")

# PARTE 5: LIMPIEZA DE OUTLIERS (CAPADO)
print("--- 5. Limpiando Outliers ---")
# Aplicamos Capado (Clipping)
df['distancia_km'] = df['distancia_km'].clip(limite_inf, limite_sup)
df.to_csv("movilidad_urbana5.csv", index=False) # Dataset Final

# PARTE 6: VISUALIZACIÓN DE RESULTADOS
print("--- Generando gráficos... ---")

# COLORES PERSONALIZADOS PARA EL MAPA DE NULOS
# 'Gainsboro' (Gris claro) para dato válido.
# 'Red' (Rojo intenso) para dato NULO.
colores_nulos = ['gainsboro', 'red'] 

# --- GRÁFICO 1: NULOS (ANTES) ---
df_nulos_sucio = pd.read_csv("movilidad_urbana2.csv")
plt.figure(1)
sns.heatmap(df_nulos_sucio.isnull(), cmap=sns.color_palette(colores_nulos), cbar=False)
plt.title('Mapa de Calor: Las líneas ROJAS son datos faltantes (Nulos)')
plt.xlabel('Variables')
plt.ylabel('Registros')
plt.tight_layout()
plt.show()

# --- GRÁFICO 2: NULOS (DESPUÉS) ---
df_nulos_limpio = pd.read_csv("movilidad_urbana3.csv")
plt.figure(2)
sns.heatmap(df_nulos_limpio.isnull(), cmap=sns.color_palette(colores_nulos), cbar=False)
plt.title('Mapa de Calor tras limpieza (Todo gris = Sin nulos)')
plt.xlabel('Variables')
plt.ylabel('Registros')
plt.tight_layout()
plt.show()

# --- GRÁFICO 3: OUTLIERS (ANTES) - SCATTER ---
df_outliers_sucio = pd.read_csv("movilidad_urbana4.csv")
mask_outliers = (df_outliers_sucio['distancia_km'] > limite_sup) | (df_outliers_sucio['distancia_km'] < limite_inf)

plt.figure(3)
# Puntos normales
plt.scatter(df_outliers_sucio.index[~mask_outliers], df_outliers_sucio.loc[~mask_outliers, 'distancia_km'],
            c='#1f77b4', alpha=0.6, label='Datos Normales')
# Puntos outliers
plt.scatter(df_outliers_sucio.index[mask_outliers], df_outliers_sucio.loc[mask_outliers, 'distancia_km'],
            c='red', s=50, label='Outliers (Errores)', zorder=5)

plt.axhline(limite_sup, color='orange', linestyle='--', label='Límite IQR')
plt.title('Detección de Outliers en "distancia_km"')
plt.xlabel('Índice del Registro')
plt.ylabel('Distancia (km)')
plt.legend()
plt.tight_layout()
plt.show()

# --- GRÁFICO 4: OUTLIERS (DESPUÉS) - SCATTER ---
df_final = pd.read_csv("movilidad_urbana5.csv")

plt.figure(4)
plt.scatter(df_final.index, df_final['distancia_km'], c='green', alpha=0.6, label='Datos Corregidos')
plt.axhline(limite_sup, color='orange', linestyle='--', label='Límite IQR')

plt.title('Distribución de "distancia_km" tras Capado (Limpieza)')
plt.xlabel('Índice del Registro')
plt.ylabel('Distancia (km)')
plt.legend()
plt.tight_layout()
plt.show()

print("Gráficos generados correctamente.")