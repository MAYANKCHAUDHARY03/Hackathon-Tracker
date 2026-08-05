import { Component, type ErrorInfo, type ReactNode } from 'react'
import { GlassPanel } from '@/components/ui/glass-panel'
import { Button } from '@/components/ui/button'

interface Props {
  children?: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex min-h-screen items-center justify-center p-4 bg-background">
          <GlassPanel className="max-w-md w-full p-8 text-center space-y-4 shadow-xl">
            <div className="mx-auto bg-destructive/10 w-16 h-16 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl" role="img" aria-label="Warning">⚠️</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-foreground">Something went wrong</h2>
            <p className="text-muted-foreground text-sm">
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <Button 
              className="mt-6 w-full"
              onClick={() => {
                this.setState({ hasError: false, error: null })
                window.location.reload()
              }}
            >
              Reload application
            </Button>
          </GlassPanel>
        </div>
      )
    }

    return this.props.children
  }
}
