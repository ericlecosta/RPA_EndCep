from geopy.geocoders import Nominatim

# Criar o geocoder
geolocator = Nominatim(user_agent="meu_app")

# Endereço completo ou parcial
endereco = "Beco Maua, Manaus"

# Obter localização
localizacao = geolocator.geocode(endereco)

if localizacao:
    print("Latitude:", localizacao.latitude)
    print("Longitude:", localizacao.longitude)
else:
    print("Endereço não encontrado")