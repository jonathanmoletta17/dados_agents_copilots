export default function ResultsTable({ rows, sort, setSort, page, setPage }: { rows: any[], sort: string, setSort: (v:string)=>void, page: number, setPage: (n:number)=>void }) {
  const glpiUrl = (id:number)=> `http://cau.ppiratini.intra.rs.gov.br/glpi/front/ticket.form.php?id=${id}`
  return (
    <div className="mt-4">
      <div className="flex gap-2 items-center">
        <button className={"px-2 py-1 border rounded "+(sort==='score'?'bg-gray-200':'')} onClick={()=>setSort('score')}>relevância</button>
        <button className={"px-2 py-1 border rounded "+(sort==='recent'?'bg-gray-200':'')} onClick={()=>setSort('recent')}>recente</button>
      </div>
      <table className="w-full mt-2 border">
        <thead>
          <tr className="bg-gray-50">
            <th className="p-2 border">ID</th>
            <th className="p-2 border">Título</th>
            <th className="p-2 border">Entidade</th>
             <th className="p-2 border">Status</th>
             <th className="p-2 border">Categoria</th>
             <th className="p-2 border">Requerente</th>
            <th className="p-2 border">Técnico</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r=> {
            const hasHighlight = !!(r.highlight && r.highlight.trim())
            const isNumericTitle = !hasHighlight && r.titulo && String(r.titulo).trim() === String(r.id)
            const plainTitle = isNumericTitle ? (r.descricao || '') : (r.titulo || '')
            return (
            <tr key={r.id} className="cursor-pointer hover:bg-gray-100" onClick={()=>window.open(r.url || glpiUrl(r.id), '_blank')}>
              <td className="p-2 border">{r.id}</td>
              <td className="p-2 border">
                {hasHighlight ? (
                  <span className="block max-w-[420px] whitespace-nowrap overflow-hidden text-ellipsis" dangerouslySetInnerHTML={{__html: r.highlight}} />
                ) : (
                  <span className="block max-w-[420px] whitespace-nowrap overflow-hidden text-ellipsis">{plainTitle}</span>
                )}
              </td>
              <td className="p-2 border">{r.entidade}</td>
              <td className="p-2 border">{r.status}</td>
              <td className="p-2 border">{r.categoria}</td>
              <td className="p-2 border">{r.requerente}</td>
              <td className="p-2 border">{r.tecnico}</td>
            </tr>
          )})}
        </tbody>
      </table>
      <div className="flex items-center gap-2 mt-2">
        <button className="px-2 py-1 border rounded" onClick={()=>setPage(Math.max(1,page-1))}>anterior</button>
        <span>página {page}</span>
        <button className="px-2 py-1 border rounded" onClick={()=>setPage(page+1)}>próxima</button>
      </div>
    </div>
  )
}