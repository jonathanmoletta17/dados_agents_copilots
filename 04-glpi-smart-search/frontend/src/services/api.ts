import axios from 'axios'

const BASE = (import.meta as any).env?.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8099`

export async function searchApi(params: Record<string, any>) {
  const r = await axios.get(`${BASE}/search`, { params })
  return r.data
}

export async function suggestApi(field: string, prefix: string) {
  const r = await axios.get(`${BASE}/suggest`, { params: { field, prefix } })
  return r.data as string[]
}

export function exportUrl(params: Record<string, any>, format: 'csv'|'xlsx') {
  const usp = new URLSearchParams({ ...params, format })
  return `${BASE}/export?${usp.toString()}`
}

export async function statsApi() {
  const r = await axios.get(`${BASE}/stats`)
  return r.data
}