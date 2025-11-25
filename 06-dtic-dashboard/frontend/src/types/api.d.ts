export interface TechnicianRankingItem {
    tecnico: string;
    tickets: number;
    nivel: string;
}

export interface GeneralStats {
    novos: number;
    em_progresso: number;
    pendentes: number;
    resolvidos: number;
}

export interface LevelStatsDetail {
    novos: number;
    em_progresso: number;
    pendentes: number;
    resolvidos: number;
    total: number;
}

export interface LevelStats {
    N1: LevelStatsDetail;
    N2: LevelStatsDetail;
    N3: LevelStatsDetail;
    N4: LevelStatsDetail;
}

export interface NewTicketItem {
    id: number | null;
    titulo: string;
    solicitante: string;
    data: string;
    prioridade?: string;
}
