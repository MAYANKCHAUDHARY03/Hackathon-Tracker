import { Bell, Search, Moon, Sun, Monitor, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUIStore } from '@/store/uiStore'
import { useAuthStore } from '@/store/authStore'
import { useNavigate } from 'react-router-dom'
import { WorkspaceSwitcher } from '@/components/workspace/WorkspaceSwitcher'

export function Topbar() {
  const { theme, setTheme } = useUIStore()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

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
        <Button variant="outline" className="w-full max-w-sm justify-start text-muted-foreground gap-2 hidden md:flex" aria-label="Search">
          <Search className="h-4 w-4" />
          <span>Search hackathons, teams... (⌘K)</span>
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          <ThemeIcon className="h-5 w-5 text-muted-foreground" />
        </Button>
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
          <Bell className="h-5 w-5 text-muted-foreground" />
          <span className="absolute top-2 right-2.5 h-2 w-2 rounded-full bg-destructive border border-background"></span>
        </Button>
        
        <div className="flex items-center gap-2 ml-4">
          <div className="h-8 w-8 rounded-full bg-primary/20 border-2 border-primary/50 flex items-center justify-center overflow-hidden cursor-pointer" title={user?.full_name || 'User'}>
            <span className="text-xs font-semibold text-primary">{user?.full_name?.charAt(0).toUpperCase() || 'U'}</span>
          </div>
          <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Log out" title="Log out">
            <LogOut className="h-5 w-5 text-muted-foreground" />
          </Button>
        </div>
      </div>
    </header>
  )
}
