import folium
from geopy.geocoders import Nominatim

# Criar o geocoder
geolocator = Nominatim(user_agent="meu_app")

# Endereço completo ou parcial
endereco = "Beco Maua Manaus"

# Obter localização
localizacao = geolocator.geocode(endereco)

if localizacao:
    print("Latitude:", localizacao.latitude)
    print("Longitude:", localizacao.longitude)
else:
    print("Endereço não encontrado")
# cria mapa centrado em São Paulo
mapa = folium.Map(location=[-3.0737361375136367, -60.00181574772833], zoom_start=12, tiles="CartoDB positron")


pontos = [
    [localizacao.latitude,  localizacao.longitude, "João Silva", 30],
    [-3.10, -60.02, "Maria Souza", 25],
    [-3.12, -60.03, "Carlos Lima", 28]
]

for lat, lon, nome, idade in pontos:
    popup_text = f"Nome: {nome}<br>Idade: {idade}"
    folium.Marker(
        location=[lat, lon],
        popup=popup_text
    ).add_to(mapa)

# salva mapa
mapa.save("mapa.html")