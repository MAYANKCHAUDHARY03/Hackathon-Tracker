import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Command } from 'cmdk'
import { Search } from 'lucide-react'
import { cn } from '@/lib/utils'
import '@/styles/cmdk.css' // Custom styles for cmdk

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const runCommand = (command: () => void) => {
    setOpen(false)
    command()
  }

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Global Command Palette"
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] sm:pt-[20vh] bg-background/80 backdrop-blur-sm p-4"
    >
      <div className="w-full max-w-2xl bg-card border border-border shadow-2xl rounded-2xl overflow-hidden glass-panel">
        <div className="flex items-center border-b border-border px-3">
          <Search className="h-5 w-5 text-muted-foreground shrink-0" />
          <Command.Input 
            placeholder="Search hackathons, teams, projects... (⌘K)" 
            className="flex h-14 w-full rounded-md bg-transparent px-3 py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>
        <Command.List className="max-h-[300px] overflow-y-auto p-2">
          <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
            No results found.
          </Command.Empty>

          <Command.Group heading="Navigation" className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
            <Command.Item 
              onSelect={() => runCommand(() => navigate('/'))}
              className={cn("relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50")}
            >
              Dashboard
            </Command.Item>
            <Command.Item 
              onSelect={() => runCommand(() => navigate('/hackathons'))}
              className={cn("relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50")}
            >
              Hackathons
            </Command.Item>
            <Command.Item 
              onSelect={() => runCommand(() => navigate('/kanban'))}
              className={cn("relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50")}
            >
              Kanban Board
            </Command.Item>
            <Command.Item 
              onSelect={() => runCommand(() => navigate('/settings'))}
              className={cn("relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50")}
            >
              Settings
            </Command.Item>
          </Command.Group>
        </Command.List>
      </div>
    </Command.Dialog>
  )
}
