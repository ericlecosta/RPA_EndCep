import pandas as pd

arq_path = r"C:\projetos\RPA_EndCep\cofap_dados.csv"

df = pd.read_csv(arq_path, sep=";", encoding="utf-8-sig", dtype={"CPF/CNS": str})
df.columns = ["equipe", "unidade", "cpf_cns","a","b","c","d","e","endereco","unidade_atend"]
df["cep"] = df["endereco"].str.extract(r"\s*(\d{5}-?\d{3})$")

df_semcep = df[
    df["cep"].isna() | ~df["cep"].str.startswith("69", na=False)
]

#print(df.info())
print(df_semcep[["endereco","cep"]])
print(len(df))
print(len(df_semcep))