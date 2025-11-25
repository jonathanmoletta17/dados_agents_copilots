export function tokenizeQuery(q: string): string[] {
    if (!q) return []
    const tokens: string[] = []
    const regex = /\"([^\"]+)\"|'([^']+)'|[^\s]+/g
    let m: RegExpExecArray | null
    while ((m = regex.exec(q)) !== null) {
        const t = (m[1] || m[2] || m[0]).trim()
        if (t) tokens.push(t)
    }
    return tokens
}

function normalize(s: string): string {
    return (s || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
}

export type HighlightPart = { text: string; highlight?: boolean }

export function computeHighlights(text: string, q: string): HighlightPart[] {
    if (!text) return [{ text: '' }]
    const terms = tokenizeQuery(q)
    if (terms.length === 0) return [{ text }]

    const normText = normalize(text)
    const ranges: Array<[number, number]> = []

    for (const term of terms) {
        const normTerm = normalize(term)
        if (!normTerm) continue
        let start = 0
        while (true) {
            const idx = normText.indexOf(normTerm, start)
            if (idx === -1) break
            ranges.push([idx, idx + normTerm.length])
            start = idx + normTerm.length
        }
    }

    if (ranges.length === 0) return [{ text }]

    // Merge overlapping ranges
    ranges.sort((a, b) => a[0] - b[0])
    const merged: Array<[number, number]> = []
    for (const r of ranges) {
        if (merged.length === 0) merged.push(r)
        else {
            const last = merged[merged.length - 1]
            if (r[0] <= last[1]) last[1] = Math.max(last[1], r[1])
            else merged.push(r)
        }
    }

    // Map normalized ranges back to original text indices
    // We assume length equality between normalized and original for basic Latin letters; for diacritics removed, positions still align for highlight span visually
    const parts: HighlightPart[] = []
    let cursor = 0
    for (const [s, e] of merged) {
        if (cursor < s) parts.push({ text: text.slice(cursor, s) })
        parts.push({ text: text.slice(s, e), highlight: true })
        cursor = e
    }
    if (cursor < text.length) parts.push({ text: text.slice(cursor) })

    return parts
}

