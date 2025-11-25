import useSWR from 'swr';
import { GeneralStats, LevelStats, TechnicianRankingItem, NewTicketItem } from '../types/api';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

interface DateRange {
    inicio: string;
    fim: string;
}

export function useGLPIData(dateRange: DateRange) {
    const qs = `?inicio=${encodeURIComponent(dateRange.inicio)}&fim=${encodeURIComponent(dateRange.fim)}`;

    // Configuração do SWR: refresh a cada 30 segundos, revalida ao focar
    const config = {
        refreshInterval: 5000, // 5 seconds (optimized for near-realtime)
        revalidateOnFocus: true,
    };

    const { data: generalStats, error: errorGeneral, isLoading: loadingGeneral, mutate: mutateGeneral } = useSWR<GeneralStats>(
        `/api/v1/dtic/metrics-gerais${qs}`,
        fetcher,
        config
    );

    const { data: levelStats, error: errorLevel, isLoading: loadingLevel, mutate: mutateLevel } = useSWR<LevelStats>(
        `/api/v1/dtic/status-niveis${qs}`,
        fetcher,
        config
    );

    const { data: technicianRanking, error: errorRanking, isLoading: loadingRanking, mutate: mutateRanking } = useSWR<TechnicianRankingItem[]>(
        `/api/v1/dtic/ranking-tecnicos${qs}`,
        fetcher,
        config
    );

    const { data: newTickets, error: errorTickets, isLoading: loadingTickets, mutate: mutateTickets } = useSWR<NewTicketItem[]>(
        '/api/v1/dtic/tickets-novos',
        fetcher,
        { ...config, refreshInterval: 5000 }
    );

    const refresh = () => {
        mutateGeneral();
        mutateLevel();
        mutateRanking();
        mutateTickets();
    };

    return {
        generalStats,
        levelStats,
        technicianRanking,
        newTickets,
        isLoading: loadingGeneral || loadingLevel || loadingRanking || loadingTickets,
        isError: errorGeneral || errorLevel || errorRanking || errorTickets,
        refresh,
    };
}
