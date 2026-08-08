import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { useDashboard } from '@/hooks/useDashboard';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import type { Workspace } from '@/types';
import { Calendar, Clock, CheckCircle2, PlayCircle, Plus, AlertCircle, RefreshCw, ChevronRight } from 'lucide-react';
import { format, isPast, isToday } from 'date-fns';
import { ProgramCreationWizard } from '@/components/hackathons/ProgramCreationWizard';

export default function Dashboard() {
  const { activeWorkspaceId, setActiveWorkspace } = useWorkspaceStore();
  const { data, isLoading, error, refetch } = useDashboard();
  const [isInitializing, setIsInitializing] = useState(!activeWorkspaceId);
  const [initError, setInitError] = useState<Error | null>(null);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  useEffect(() => {
    async function initWorkspace() {
      if (activeWorkspaceId) return;
      try {
        const workspaces = await apiClient.get<Workspace[]>('/workspaces');
        if (workspaces.length > 0) {
          setActiveWorkspace(workspaces[0].id);
        }
      } catch (err: any) {
        setInitError(err instanceof Error ? err : new Error('Failed to load workspaces'));
      } finally {
        setIsInitializing(false);
      }
    }
    initWorkspace();
  }, [activeWorkspaceId, setActiveWorkspace]);

  if (isInitializing || (isLoading && !error && !data)) {
    return (
      <div className="space-y-6">
        <div>
          <div className="h-9 w-48 bg-secondary/50 rounded-md animate-pulse"></div>
          <div className="h-5 w-72 bg-secondary/30 rounded-md animate-pulse mt-2"></div>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <GlassPanel className="h-64 animate-pulse bg-secondary/20">{null}</GlassPanel>
          <GlassPanel className="h-64 animate-pulse bg-secondary/20">{null}</GlassPanel>
          <GlassPanel className="h-64 animate-pulse bg-secondary/20">{null}</GlassPanel>
        </div>
      </div>
    );
  }

  if (initError || error) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <div className="p-4 bg-destructive/10 text-destructive rounded-full">
          <AlertCircle className="h-8 w-8" />
        </div>
        <h2 className="text-xl font-semibold">Something went wrong</h2>
        <p className="text-muted-foreground text-center max-w-md">
          {initError?.message || error?.message}
        </p>
        <Button onClick={() => { setInitError(null); refetch(); }} variant="outline" className="gap-2">
          <RefreshCw className="h-4 w-4" /> Try Again
        </Button>
      </div>
    );
  }

  if (data && data.total_non_archived === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] space-y-6 max-w-md mx-auto text-center">
        <div className="p-6 bg-primary/10 text-primary rounded-full">
          <Calendar className="h-12 w-12" />
        </div>
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-2">Welcome to HackTracker</h2>
          <p className="text-muted-foreground">
            You don't have any programs yet. Create your first program to get started tracking projects, deadlines, and teams.
          </p>
        </div>
        <Button size="lg" className="gap-2" onClick={() => setIsWizardOpen(true)}>
          <Plus className="h-5 w-5" />
          Create Program
        </Button>
        <ProgramCreationWizard open={isWizardOpen} onOpenChange={setIsWizardOpen} onSuccess={refetch} />
      </div>
    );
  }

  const renderDeadlineStatus = (dateString: string) => {
    const date = new Date(dateString);
    if (isPast(date) && !isToday(date)) {
      return <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-destructive/10 text-destructive">Overdue</span>;
    }
    if (isToday(date)) {
      return <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-500">Today</span>;
    }
    return <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Upcoming</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Overview of your programs and upcoming deadlines.</p>
        </div>
        <Button onClick={refetch} variant="ghost" size="icon" title="Refresh">
          <RefreshCw className="h-5 w-5 text-muted-foreground" />
        </Button>
      </div>
      
      <div className="grid gap-6 md:grid-cols-3">
        {/* Status Breakdown */}
        <GlassPanel className="md:col-span-3 lg:col-span-1 p-6 space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-primary/20 rounded-lg">
              <PlayCircle className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-lg font-semibold tracking-tight">Status Breakdown</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-secondary/30 flex flex-col justify-center items-center text-center">
              <span className="text-3xl font-bold text-primary">{data?.total_active}</span>
              <span className="text-sm text-muted-foreground font-medium mt-1">Active</span>
            </div>
            <div className="p-4 rounded-xl bg-secondary/30 flex flex-col justify-center items-center text-center">
              <span className="text-3xl font-bold text-foreground">{data?.total_upcoming}</span>
              <span className="text-sm text-muted-foreground font-medium mt-1">Upcoming</span>
            </div>
            <div className="p-4 rounded-xl bg-secondary/30 flex flex-col justify-center items-center text-center">
              <span className="text-3xl font-bold text-muted-foreground">{data?.total_completed}</span>
              <span className="text-sm text-muted-foreground font-medium mt-1">Completed</span>
            </div>
            <div className="p-4 rounded-xl bg-secondary/30 flex flex-col justify-center items-center text-center">
              <span className="text-3xl font-bold text-foreground">{data?.total_non_archived}</span>
              <span className="text-sm text-muted-foreground font-medium mt-1">Total</span>
            </div>
          </div>
          
          {data?.nearest_upcoming_event && (
            <div className="mt-6 pt-6 border-t border-border/50">
              <h3 className="text-sm font-medium text-muted-foreground mb-3">Nearest Event</h3>
              <Link to={`/hackathons/${data.nearest_upcoming_event.id}`} className="block group">
                <div className="p-3 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors border border-primary/10">
                  <p className="font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                    {data.nearest_upcoming_event.name}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    Starts {format(new Date(data.nearest_upcoming_event.start_date), 'MMM d, yyyy')}
                  </p>
                </div>
              </Link>
            </div>
          )}
        </GlassPanel>

        {/* Upcoming Deadlines */}
        <GlassPanel className="md:col-span-1 lg:col-span-1 p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Clock className="h-5 w-5 text-orange-500" />
            </div>
            <h2 className="text-lg font-semibold tracking-tight">Registration Deadlines</h2>
          </div>
          <div className="space-y-4 flex-1">
            {data?.upcoming_deadlines && data.upcoming_deadlines.length > 0 ? (
              data.upcoming_deadlines.map((item) => (
                <Link key={`deadline-${item.id}`} to={`/hackathons/${item.id}`} className="block group">
                  <div className="flex items-start justify-between p-3 rounded-lg hover:bg-secondary/40 transition-colors">
                    <div className="overflow-hidden mr-3">
                      <p className="font-medium text-sm truncate group-hover:text-primary transition-colors">{item.name}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {format(new Date(item.registration_deadline), 'MMM d, h:mm a')}
                      </p>
                    </div>
                    <div className="shrink-0 flex items-center gap-2">
                      {renderDeadlineStatus(item.registration_deadline)}
                      <ChevronRight className="h-4 w-4 text-muted-foreground/50 group-hover:text-foreground transition-colors" />
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center h-32 text-center">
                <CheckCircle2 className="h-8 w-8 text-muted-foreground/50 mb-2" />
                <p className="text-sm text-muted-foreground">No upcoming deadlines.</p>
              </div>
            )}
          </div>
          
          <div className="mt-6 pt-6 border-t border-border/50">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" /> Action Items
            </h3>
            <div className="space-y-2">
              <div className="p-3 rounded-lg bg-secondary/10 border border-primary/10">
                <p className="text-sm font-medium">Complete Submission</p>
                <p className="text-xs text-muted-foreground">For Phase 1 Round</p>
              </div>
            </div>
          </div>
        </GlassPanel>

        {/* Recent Activity */}
        <GlassPanel className="md:col-span-1 lg:col-span-1 p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <RefreshCw className="h-5 w-5 text-blue-500" />
            </div>
            <h2 className="text-lg font-semibold tracking-tight">Recently Updated</h2>
          </div>
          <div className="space-y-2 flex-1">
            {data?.recently_updated && data.recently_updated.length > 0 ? (
              data.recently_updated.map((item) => (
                <Link key={`recent-${item.id}`} to={`/hackathons/${item.id}`} className="block group">
                  <div className="p-3 rounded-lg bg-secondary/20 hover:bg-secondary/50 transition-colors border border-transparent hover:border-border/50">
                    <div className="flex justify-between items-center mb-1">
                      <p className="font-medium text-sm truncate pr-2 group-hover:text-primary transition-colors">{item.name}</p>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground bg-background px-1.5 py-0.5 rounded">
                        {item.status}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Updated {format(new Date(item.updated_at), 'MMM d')}
                    </p>
                  </div>
                </Link>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">No recent activity.</p>
            )}
          </div>
        </GlassPanel>
      </div>

      <ProgramCreationWizard open={isWizardOpen} onOpenChange={setIsWizardOpen} onSuccess={refetch} />
    </div>
  );
}
