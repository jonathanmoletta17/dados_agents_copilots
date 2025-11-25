-- Test query similar to what the API uses
SELECT 
    glpi_id as id,
    titulo,
    descricao_md as descricao,
    status,
    prioridade,
    categoria,
    entidade,
    tecnico,
    grupo,
    requerente,
    to_char(criado_em, 'YYYY-MM-DD HH24:MI:SS') as data_criacao,
    to_char(atualizado_em, 'YYYY-MM-DD HH24:MI:SS') as data_modificacao,
    to_char(solucionado_em, 'YYYY-MM-DD HH24:MI:SS') as data_solucao,
    to_char(fechado_em, 'YYYY-MM-DD HH24:MI:SS') as data_fechamento,
    '' as motivo_pendencia,
    url,
    '' as highlight,
    0.0 as score
FROM sis.tickets
WHERE is_deleted = false
ORDER BY atualizado_em DESC
LIMIT 20 OFFSET 0;
