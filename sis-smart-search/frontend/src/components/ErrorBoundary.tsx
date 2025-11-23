import { Component, ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { hasError: boolean, error?: any }

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) { super(props); this.state = { hasError: false } }
  static getDerivedStateFromError(error: any) { return { hasError: true, error } }
  componentDidCatch(error: any) { console.error('Erro na UI:', error) }
  render() {
    if (this.state.hasError) {
      const msg = this.state.error?.message || String(this.state.error)
      const stack = this.state.error?.stack
      return (
        <div style={{ padding: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Falha ao renderizar a interface</div>
          <div style={{ color: '#b91c1c', marginBottom: 8 }}>{msg}</div>
          {stack && <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#374151' }}>{stack}</pre>}
        </div>
      )
    }
    return this.props.children
  }
}