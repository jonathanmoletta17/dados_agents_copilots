# Análise de Dados GLPI

Projeto de análise e limpeza de dados de tickets do GLPI.

## Estrutura
- `data/raw/` - Dados brutos (XLSX originais)
- `data/processed/` - Dados limpos (XLSX processados)
- `data/reports/` - Relatórios gerados
- `scripts/` - Scripts de limpeza e análise

## Uso
```bash
# Limpar dados de tickets (XLSX)
python limpar_tickets_xlsx.py

# Arquivo principal: todos_tickets_atual_limpo.xlsx
```

## Resultados
- **Total de tickets processados**: 11,030
- **Redução de caracteres**: 5.0% (155,128 caracteres removidos)
- **Tickets com estruturas de formulário**: 2,527
- **Formato**: Apenas XLSX (sem CSVs)
