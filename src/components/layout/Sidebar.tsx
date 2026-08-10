import { NavLink } from 'react-router-dom'
import { useUIStore } from '@/store/uiStore'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  CalendarDays, 
  KanbanSquare, 
  LineChart, 
  Users, 
  FolderGit2, 
  KeyRound, 
  Settings,
  Menu,
  Trophy,
  Building,
  Network,
  Sparkles
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/hackathons', label: 'Programs', icon: Trophy },
  { path: '/calendar', label: 'Calendar', icon: CalendarDays },
  { path: '/kanban', label: 'Kanban', icon: KanbanSquare },
  { path: '/analytics', label: 'Analytics', icon: LineChart },
  { path: '/teams', label: 'Team Database', icon: Users },
  { path: '/projects', label: 'Project Database', icon: FolderGit2 },
  { path: '/graph', label: 'Innovation Graph', icon: Network },
  { path: '/opportunities', label: 'Opportunities', icon: Sparkles },
  { path: '/vault', label: 'API Vault', icon: KeyRound },
  { path: '/portfolio', label: 'Portfolio', icon: Building },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useUIStore()

  return (
    <aside 
      className={cn(
        "glass-panel fixed left-0 top-0 z-40 h-screen transition-all duration-300 ease-custom-bezier",
        isSidebarOpen ? "w-64" : "w-20"
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b border-border/50">
        <div className={cn("flex items-center gap-2 overflow-hidden transition-all", !isSidebarOpen && "w-0 opacity-0")}>
          <div className="bg-primary/20 p-1.5 rounded-lg">
            <Trophy className="h-5 w-5 text-primary" />
          </div>
          <span className="font-semibold whitespace-nowrap text-foreground tracking-tight">HackTracker</span>
        </div>
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="shrink-0" aria-label="Toggle Sidebar">
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      <nav className="p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group",
              isActive 
                ? "bg-primary text-primary-foreground font-medium" 
                : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
            )}
            title={!isSidebarOpen ? item.label : undefined}
          >
            <item.icon className={cn("h-5 w-5 shrink-0 transition-transform", !isSidebarOpen && "group-hover:scale-110")} />
            {isSidebarOpen && (
              <span className="truncate">{item.label}</span>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
