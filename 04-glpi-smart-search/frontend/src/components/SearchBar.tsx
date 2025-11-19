import { useEffect, useState } from 'react'
import { suggestApi } from '../services/api'

export default function SearchBar({ value, onChange }: { value: string, onChange: (v: string)=>void }) {
  const [prefix, setPrefix] = useState('')
  const [sugs, setSugs] = useState<string[]>([])
  useEffect(()=>{
    const i = setTimeout(async ()=>{
      if (prefix.length >= 2) {
        try {
          const a = await suggestApi('entidade', prefix)
          setSugs(a)
        } catch (e) {
          console.error('Falha ao sugerir entidade:', e)
          setSugs([])
        }
      } else setSugs([])
    }, 250)
    return ()=>clearTimeout(i)
  },[prefix])
  return (
    <div className="flex gap-2 items-center">
      <input className="border rounded px-3 py-2 w-full" placeholder={"busque em texto e use filtros: status:solucionado tecnico:edson entidade:\"casa civil\""} value={value} onChange={e=>onChange(e.target.value)} />
      <input className="border rounded px-2 py-2 w-52" placeholder="autocomplete entidade" value={prefix} onChange={e=>setPrefix(e.target.value)} />
      {sugs.length>0 && (
        <div className="absolute mt-20 bg-white border rounded shadow p-2 w-52">
          {sugs.map(s=> (
            <div key={s} className="cursor-pointer hover:bg-gray-100 px-2" onClick={()=>onChange(value ? value+` entidade:${s}` : `entidade:${s}`)}>{s}</div>
          ))}
        </div>
      )}
    </div>
  )
}