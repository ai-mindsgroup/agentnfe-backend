"""
Script para comparar os arquivos CSV de Notas Fiscais
"""
import pandas as pd
import os

print("=" * 80)
print("COMPARAÇÃO: 202505_NFe_NotaFiscal.csv vs 202505_NFe_NotaFiscalItem.csv")
print("=" * 80)

f1 = 'data/202505_NFe_NotaFiscal.csv'
f2 = 'data/202505_NFe_NotaFiscalItem.csv'

# Tamanho dos arquivos
print(f"\n📊 TAMANHO DOS ARQUIVOS:")
print(f"  • {f1}: {os.path.getsize(f1) / (1024**2):.2f} MB")
print(f"  • {f2}: {os.path.getsize(f2) / (1024**2):.2f} MB")

# Tentar diferentes encodings
encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
df1 = None
df2 = None
encoding_used = None

for enc in encodings:
    try:
        df1 = pd.read_csv(f1, nrows=10, encoding=enc, sep=';')
        df2 = pd.read_csv(f2, nrows=10, encoding=enc, sep=';')
        encoding_used = enc
        print(f"\n✅ Encoding detectado: {enc}")
        break
    except Exception as e:
        continue

if df1 is None or df2 is None:
    print("❌ Não foi possível ler os arquivos com os encodings testados")
    exit(1)

# Análise do arquivo NotaFiscal
print("\n" + "=" * 80)
print("📄 ARQUIVO: 202505_NFe_NotaFiscal.csv")
print("=" * 80)
print(f"Total de colunas: {len(df1.columns)}")
print(f"\nColunas:")
for i, col in enumerate(df1.columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\n📊 Tipos de dados:")
print(df1.dtypes.to_string())

print(f"\n📝 Primeiras 3 linhas (amostra):")
print(df1.head(3).to_string())

# Análise do arquivo NotaFiscalItem
print("\n" + "=" * 80)
print("📄 ARQUIVO: 202505_NFe_NotaFiscalItem.csv")
print("=" * 80)
print(f"Total de colunas: {len(df2.columns)}")
print(f"\nColunas:")
for i, col in enumerate(df2.columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\n📊 Tipos de dados:")
print(df2.dtypes.to_string())

print(f"\n📝 Primeiras 3 linhas (amostra):")
print(df2.head(3).to_string())

# Comparação
print("\n" + "=" * 80)
print("🔍 ANÁLISE COMPARATIVA")
print("=" * 80)

# Colunas em comum
colunas_comuns = set(df1.columns) & set(df2.columns)
print(f"\n✅ Colunas em comum ({len(colunas_comuns)}):")
for col in sorted(colunas_comuns):
    print(f"  • {col}")

# Colunas exclusivas
colunas_exclusivas_1 = set(df1.columns) - set(df2.columns)
print(f"\n📌 Colunas exclusivas de NotaFiscal ({len(colunas_exclusivas_1)}):")
for col in sorted(colunas_exclusivas_1):
    print(f"  • {col}")

colunas_exclusivas_2 = set(df2.columns) - set(df1.columns)
print(f"\n📌 Colunas exclusivas de NotaFiscalItem ({len(colunas_exclusivas_2)}):")
for col in sorted(colunas_exclusivas_2):
    print(f"  • {col}")

# Resumo
print("\n" + "=" * 80)
print("📋 RESUMO")
print("=" * 80)
print(f"NotaFiscal:     {len(df1.columns)} colunas")
print(f"NotaFiscalItem: {len(df2.columns)} colunas")
print(f"Em comum:       {len(colunas_comuns)} colunas")
print(f"Exclusivas NF:  {len(colunas_exclusivas_1)} colunas")
print(f"Exclusivas NFI: {len(colunas_exclusivas_2)} colunas")
print("=" * 80)
