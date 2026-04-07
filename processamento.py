import pandas as pd
from opencage.geocoder import OpenCageGeocode
#from geopy.exc import GeocoderTimedOut
import time

# 1 Inicializa o geocodificador
API_KEY = "ef9362e916f84829ac8467ff274a05dc"  # substitua pela sua chave
geocoder = OpenCageGeocode(API_KEY)

# 2 Função de geocoding
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


def tratar_dados(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, sep=";", encoding="utf-8-sig", dtype={"CPF/CNS": str})

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

    print('df:',len(df))
    print('df_com_end:',len(df_tend))
    print('df_sem_cep:',len(df_fcep))
    print('df_com_cep:',len(df_ccep))
    print('df_area:',len(df_area))
    print('df_area_sem_cep:',len(df_area[df_area["cep"].isna()]))
    print('df_area_lg_lt:',len(df_amostra[(df_amostra["latitude"].notna() & df_amostra["longitude"].notna())]))
    print(df_amostra[['cpf_cns','endereco','cep','latitude','longitude']].head(20))

    return df_amostra

