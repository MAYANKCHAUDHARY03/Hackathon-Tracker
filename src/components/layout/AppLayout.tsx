import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'
import { CommandPalette } from './CommandPalette'
import { FeedbackWidget } from '@/components/feedback/FeedbackWidget'
import { useUIStore } from '@/store/uiStore'
import { cn } from '@/lib/utils'

export function AppLayout() {
  const { isSidebarOpen, theme } = useUIStore()

  // Apply theme to document
  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      root.classList.add(systemTheme)
      return
    }

    root.classList.add(theme)
  }, [theme])

  return (
    <div className="min-h-screen bg-background bg-gradient-to-br from-background via-background to-secondary/30 text-foreground flex overflow-hidden">
      <Sidebar />
      <div 
        className={cn(
          "flex-1 flex flex-col min-w-0 transition-all duration-300 ease-custom-bezier",
          isSidebarOpen ? "ml-64" : "ml-20"
        )}
      >
        <Topbar />
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <CommandPalette />
      <FeedbackWidget />
    </div>
  )
}
