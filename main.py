from download import baixar_arquivo
from processamento import tratar_dados
from mapa import gerar_mapa
import os

def main():
    # # 1. Download

    caminho = baixar_arquivo()

    print(caminho)

    #caminho = r"C:\projetos\RPA_EndCep\cofap.dados.csv"
    #caminho = r"C:\Users\Turma02\pyteste\RPA_EndCep\cofap_dados.csv"

    # 2. Tratamento
    df = tratar_dados(caminho)

    # # 3. Mapa
    mapa = gerar_mapa(df)

    # 4. Salvar
    if mapa:
        mapa.save('mapa_enderecos.html')
   

    print("Mapa gerado com sucesso!")


if __name__ == "__main__":
    main()