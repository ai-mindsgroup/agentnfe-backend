import pandas as pd

# Ler CSV
df = pd.read_csv('data/202505_NFe_NotaFiscalItem.csv', encoding='latin-1', sep=';')

# Verificar tamanhos máximos
print('Max lengths por coluna:')
for col in df.select_dtypes(include='object').columns:
    max_len = df[col].astype(str).str.len().max()
    if max_len > 200:
        print(f'{col}: {max_len} ⚠️ EXCEDE 200!')
    else:
        print(f'{col}: {max_len}')
