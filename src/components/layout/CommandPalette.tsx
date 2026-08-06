import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Command } from 'cmdk'
import { Search, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useSearch } from '@/hooks/useSearch'
import '@/styles/cmdk.css' // Custom styles for cmdk

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()
  
  const { data: searchData, isLoading } = useSearch(searchQuery)

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
      <div className="w-full max-w-2xl bg-card border border-border shadow-2xl rounded-2xl overflow-hidden glass-panel flex flex-col">
        <div className="flex items-center border-b border-border px-3">
          <Search className="h-5 w-5 text-muted-foreground shrink-0" />
          <Command.Input 
            placeholder="Search hackathons, teams, projects... (⌘K)" 
            className="flex h-14 w-full rounded-md bg-transparent px-3 py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            value={searchQuery}
            onValueChange={setSearchQuery}
          />
          {isLoading && <Loader2 className="h-5 w-5 animate-spin text-muted-foreground shrink-0" />}
        </div>
        <Command.List className="max-h-[300px] overflow-y-auto p-2">
          {searchQuery && !isLoading && (!searchData || searchData.results.length === 0) && (
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found for "{searchQuery}".
            </Command.Empty>
          )}

          {searchData && searchData.results.length > 0 && (
            <Command.Group heading="Search Results" className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
              {searchData.results.map((result) => (
                <Command.Item
                  key={result.id}
                  onSelect={() => runCommand(() => navigate(result.url))}
                  className={cn("relative flex flex-col cursor-pointer select-none rounded-sm px-2 py-2 outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50")}
                >
                  <div className="font-medium text-sm text-foreground">{result.title}</div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground">
                      {result.type}
                    </span>
                    {result.description && (
                      <span className="text-xs text-muted-foreground truncate max-w-[400px]">
                        {result.description}
                      </span>
                    )}
                  </div>
                </Command.Item>
              ))}
            </Command.Group>
          )}

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
