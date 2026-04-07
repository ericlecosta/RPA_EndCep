import folium
from folium.plugins import MarkerCluster
import pandas as pd

def gerar_mapa(df, lat_col='latitude', lon_col='longitude', popup_col='endereco'):
    cidade_centro = [-3.119, -60.021]  # Manaus

    # Filtra apenas registros com latitude e longitude válidas
    df_map = df[df[lat_col].notna() & df[lon_col].notna()]
    
    # Se não houver pontos válidos, retorna None
    if df_map.empty:
        print("Não há registros com coordenadas válidas para plotar.")
        return None

    mapa = folium.Map(
        location=[df_map[lat_col].mean(), df_map[lon_col].mean()] if df_map.shape[0] > 0 else cidade_centro,
        zoom_start=12,
        tiles="CartoDB positron"
    )

    cluster = MarkerCluster().add_to(mapa)

    for _, row in df_map.iterrows():
        if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
            folium.Marker(
                location=[row[lat_col], row[lon_col]],
                popup=row[popup_col],
                icon=folium.Icon(color='blue')
            ).add_to(cluster)

    return mapa