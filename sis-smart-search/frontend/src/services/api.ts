import axios from 'axios'
const BASE = (import.meta as any).env?.VITE_API_BASE_URL || '/api'
export async function searchApi(params: Record<string, any>) { const r = await axios.get(`${BASE}/v1/sis/search`, { params }); return r.data }
export async function suggestApi(field: string, prefix: string) { const r = await axios.get(`${BASE}/v1/sis/search/suggest`, { params: { field, prefix } }); return r.data as string[] }
export function exportUrl(params: Record<string, any>, format: 'csv' | 'xlsx') { const usp = new URLSearchParams({ ...params, format }); return `${BASE}/v1/sis/search/export?${usp.toString()}` }
export async function statsApi() { const r = await axios.get(`${BASE}/v1/sis/dashboard/stats-gerais`); return r.data }
