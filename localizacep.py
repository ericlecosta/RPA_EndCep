import pandas as pd
#from geopy.geocoders import Nominatim
from opencage.geocoder import OpenCageGeocode
from geopy.exc import GeocoderTimedOut
import folium
from folium.plugins import MarkerCluster
import time

#geolocator = Nominatim(user_agent="meu_app", timeout=10)

# 1️⃣ Inicializa o geocodificador
API_KEY = "ef9362e916f84829ac8467ff274a05dc"  # substitua pela sua chave
geocoder = OpenCageGeocode(API_KEY)

# 2️⃣ Função de geocoding
def geocodificar(endereco, cep=None, cidade="Manaus", estado="AM", pais="Brasil"):
    """
    Retorna latitude e longitude usando OpenCage.
    Usa CEP se disponível, caso contrário endereço completo.
    """
    consulta = None
    if pd.notna(cep):
        cep_str = str(cep).zfill(8)  # garante 8 dígitos
        print(f"{cep_str[:5]}-{cep_str[5:]}")
        consulta = f"{cep_str[:5]}-{cep_str[5:]}, {cidade}, {estado}, {pais}"
    elif pd.notna(endereco):
        consulta = f"{endereco}, {cidade}, {estado}, {pais}"

    if consulta:
        try:
            results = geocoder.geocode(consulta, no_annotations='1', limit=1)
            if results:
                lat = results[0]['geometry']['lat']
                lon = results[0]['geometry']['lng']
                return lat, lon
        except Exception as e:
            print(f"Erro OpenCage: {e}")
            time.sleep(1)  # respeitar limite de 1 requisição por segundo
    return pd.NA, pd.NA

#ef9362e916f84829ac8467ff274a05dc

# def geocodificar(endereco, cep=None, cidade="Manaus", estado="AM", pais="Brasil"):
#     """
#     Retorna latitude e longitude usando geopy.
#     - Se houver CEP, usa apenas CEP + cidade + estado + país.
#     - Caso contrário, usa endereço completo + cidade + estado + país.
#     """
#     if pd.isna(endereco) and pd.isna(cep):
#         return pd.NA, pd.NA

#     if pd.notna(cep):
#         consulta = f"{cep}-{cep[5:]}, {cidade}, {estado}, {pais}"
#     else:
#         consulta = f"{endereco}, {cidade}, {estado}, {pais}"
    
#     try:
#         location = geolocator.geocode(consulta)
#         time.sleep(2)  # respeitar limites do Nominatim
#         if location:
#             return location.latitude, location.longitude
#         else:
#             return pd.NA, pd.NA
#     except GeocoderTimedOut:
#         return pd.NA, pd.NA
    
def gerar_mapa(df, lat_col='latitude', lon_col='longitude', popup_col='endereco',
               cidade_centro=[-3.1190, -60.0217], zoom_start=12):
    """
    Gera um mapa Folium interativo a partir de um DataFrame.
    
    Parâmetros:
    - df: DataFrame com dados geográficos
    - lat_col: nome da coluna de latitude
    - lon_col: nome da coluna de longitude
    - popup_col: coluna para mostrar ao clicar no marcador
    - cidade_centro: lista [lat, lon] para centralizar o mapa se média não for desejada
    - zoom_start: nível inicial de zoom do mapa
    
    Retorna:
    - objeto folium.Map
    """
    
    # Filtra apenas registros com latitude e longitude válidas
    df_map = df[df[lat_col].notna() & df[lon_col].notna()]
    
    # Se não houver pontos válidos, retorna None
    if df_map.empty:
        print("Não há registros com coordenadas válidas para plotar.")
        return None
    
    # Cria o mapa centralizado na média das coordenadas ou no centro fornecido
    mapa = folium.Map(
        location=[df_map[lat_col].mean(), df_map[lon_col].mean()] if df_map.shape[0] > 0 else cidade_centro,
        zoom_start=zoom_start,tiles="CartoDB positron"
    )
    
    # Cria cluster para agrupar marcadores próximos
    cluster = MarkerCluster().add_to(mapa)
    
    # Adiciona marcadores
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=row[popup_col],
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(cluster)

    # for _, row in df_map.iterrows():
    #     folium.Marker(
    #     location=[row[lat_col], row[lon_col]],
    #     popup=row[popup_col],
    #     icon=folium.Icon(color='blue', icon='info-sign')
    # ).add_to(mapa)  # adiciona direto no mapa, sem cluster
    
    return mapa

# Tratamento do df e csv--------------------------------------------
#arq_path = r"C:\projetos\RPA_EndCep\cofap_dados.csv"
arq_path = r"C:\Users\Turma02\pyteste\RPA_EndCep\cofap_dados.csv"

df = pd.read_csv(arq_path, sep=";", encoding="utf-8-sig", dtype={"CPF/CNS": str})
df.columns = ["equipe", "unidade", "cpf_cns","a","b","c","d","e","endereco","unidade_atend"]
df["no_end"] = df['endereco'].str.strip()

# buscar apenas registros com endereço
df_tend = df[~df['no_end'].isin(['-', ''])].copy()

#separar cep
df_tend["cep"] = df_tend["endereco"].str.extract(r"\s*(\d{5}-?\d{3})$")

#dfs para contabilizar com cep e sem cep
df_fcep = df_tend[df_tend["cep"].isna()]
df_ccep = df_tend[df_tend["cep"].notna()]

# criar df para um bairro
df_area = df_tend[df_tend['endereco'].str.contains('jorge teixeira', case=False)]

#criar amostras com 10 com cep e 10 sem cep
amostra_com_cep = df_area[df_area['cep'].notna()].sample(n=10, random_state=42)
amostra_sem_cep = df_area[df_area['cep'].isna()].sample(n=10, random_state=42)

df_amostra = pd.concat([amostra_com_cep, amostra_sem_cep])
df_amostra['latitude'] = pd.NA
df_amostra['longitude'] = pd.NA

print('#Pesquisando coordenadas')
# Aplica função linha a linha trazendo as coordenadas
df_amostra[['latitude', 'longitude']] = df_amostra.apply(
    lambda row: geocodificar(row['endereco'], row['cep']),
    axis=1,
    result_type='expand'
)

#criar mapa chamando a função
mapa = gerar_mapa(df_amostra)

if mapa:
    mapa.save('mapa_enderecos.html')

#print(df.info())
#print(df_fcep[["endereco","cep"]])
#df_fcep.to_csv('falta_cep.csv')

print('df:',len(df))
print('df_com_end:',len(df_tend))
print('df_sem_cep:',len(df_fcep))
print('df_com_cep:',len(df_ccep))
print('df_area:',len(df_area))
print('df_area_sem_cep:',len(df_area[df_area["cep"].isna()]))
print('df_area_lg_lt:',len(df_amostra[(df_amostra["latitude"].notna() & df_amostra["longitude"].notna())]))
print(df_amostra[['cpf_cns','endereco','cep','latitude','longitude']].head(20))
