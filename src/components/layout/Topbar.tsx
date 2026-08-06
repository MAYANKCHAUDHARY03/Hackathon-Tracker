import { Search, Moon, Sun, Monitor, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUIStore } from '@/store/uiStore'
import { useAuthStore } from '@/store/authStore'
import { useNavigate } from 'react-router-dom'
import { WorkspaceSwitcher } from '@/components/workspace/WorkspaceSwitcher'
import { NotificationBadge } from '@/components/notifications/NotificationBadge'
import { SearchModal } from '@/components/Search/SearchModal'
import { useState, useEffect } from 'react'

export function Topbar() {
  const { theme, setTheme } = useUIStore()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [isSearchOpen, setIsSearchOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsSearchOpen(true)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Simple cycle theme
  const toggleTheme = () => {
    if (theme === 'light') setTheme('dark')
    else if (theme === 'dark') setTheme('system')
    else setTheme('light')
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const ThemeIcon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Monitor

  return (
    <header className="glass-panel sticky top-0 z-30 flex h-16 items-center justify-between px-6 border-b border-border/50 shadow-sm backdrop-blur-md">
      <div className="flex items-center gap-4 flex-1">
        <WorkspaceSwitcher />
        <Button variant="outline" className="w-full max-w-sm justify-start text-muted-foreground gap-2 hidden md:flex" aria-label="Search" onClick={() => setIsSearchOpen(true)}>
          <Search className="h-4 w-4" />
          <span>Search hackathons, teams... (⌘K)</span>
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          <ThemeIcon className="h-5 w-5 text-muted-foreground" />
        </Button>
        <NotificationBadge />
        
        <div className="flex items-center gap-2 ml-4">
          <div 
            className="h-8 w-8 rounded-full bg-primary/20 border-2 border-primary/50 flex items-center justify-center overflow-hidden cursor-pointer hover:bg-primary/30 transition-colors" 
            title="View Portfolio"
            onClick={() => user?.id && navigate(`/users/${user.id}/portfolio`)}
          >
            <span className="text-xs font-semibold text-primary">{user?.full_name?.charAt(0).toUpperCase() || 'U'}</span>
          </div>
          <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Log out" title="Log out">
            <LogOut className="h-5 w-5 text-muted-foreground" />
          </Button>
        </div>
      </div>
      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </header>
  )
}
