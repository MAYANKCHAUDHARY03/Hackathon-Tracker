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
  Key,
  Banknote,
  Network,
  Activity,
  Sparkles,
  Store,
  Globe,
  Bot,
  BrainCircuit,
  Target,
  Telescope,
  Lightbulb,
  ShieldCheck,
  Zap,
  Terminal
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/operations-center', label: 'Operations Center', icon: Activity },
  { path: '/hackathons', label: 'Programs', icon: Trophy },
  { path: '/calendar', label: 'Calendar', icon: CalendarDays },
  { path: '/kanban', label: 'Kanban', icon: KanbanSquare },
  { path: '/analytics', label: 'Analytics', icon: LineChart },
  { path: '/teams', label: 'Team Database', icon: Users },
  { path: '/projects', label: 'Project Database', icon: FolderGit2 },
  { path: '/graph', label: 'Innovation Graph', icon: Network },
  { path: '/knowledge-graph', label: 'Knowledge Graph', icon: Network },
  { path: '/challenge-exchange', label: 'Challenge Exchange', icon: Sparkles },
  { path: '/opportunities', label: 'Opportunities', icon: Sparkles },
  { path: '/vault', label: 'API Vault', icon: KeyRound },
  { path: '/portfolio', label: 'Portfolio', icon: Building },
  { path: '/portable-identity', label: 'Innovation Passport', icon: Key },
  { path: '/financing-intelligence', label: 'Financing', icon: Banknote },
  { path: '/marketplace', label: 'Marketplace', icon: Store },
  { path: '/copilot', label: 'AI Copilot', icon: Bot },
  { path: '/forecasting', label: 'Forecasting', icon: BrainCircuit },
  { path: '/impact', label: 'Impact Measurement', icon: Target },
  { path: '/incubation', label: 'Incubation', icon: Lightbulb },
  { path: '/observatory', label: 'Global Observatory', icon: Globe },
  { path: '/federation', label: 'Ecosystem Federation', icon: Network },
  { path: '/governance', label: 'Governance', icon: ShieldCheck },
  { path: '/automation', label: 'Workflow Automation', icon: Zap },
  { path: '/integrations', label: 'Integrations', icon: Network },
  { path: '/developer', label: 'Developer Portal', icon: Terminal },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useUIStore()

  return (
    <aside 
      className={cn(
        "glass-panel fixed left-0 top-0 z-40 h-screen flex flex-col transition-all duration-300 ease-custom-bezier",
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

      <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
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
