import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { hackathonApi } from '@/api/hackathonApi';
import type { Hackathon } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Trophy, Plus, Calendar, Clock, ArrowRight, Activity } from 'lucide-react';
import { format, isPast, isFuture } from 'date-fns';
import { ProgramCreationWizard } from '@/components/hackathons/ProgramCreationWizard';
import { ProgramSimulationEngine } from '@/components/hackathons/ProgramSimulationEngine';

export default function Hackathons() {
  const navigate = useNavigate();
  const { activeWorkspaceId } = useWorkspaceStore();
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  const fetchHackathons = async () => {
    if (!activeWorkspaceId) return;
    setIsLoading(true);
    setError(null);
    try {
      const raw: any = await hackathonApi.getHackathons(activeWorkspaceId);
      const list = Array.isArray(raw) ? raw : Array.isArray(raw?.items) ? raw.items : Array.isArray(raw?.data) ? raw.data : [];
      setHackathons(list);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error('Failed to load programs'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHackathons();
  }, [activeWorkspaceId]);

  const getStatusDisplay = (hackathon: Hackathon) => {
    if ((hackathon as any).status === 'draft') return { label: 'Draft', color: 'bg-secondary text-secondary-foreground' };
    
    const startDate = new Date(hackathon.start_date);
    const endDate = new Date(hackathon.end_date);
    
    if (isFuture(startDate)) {
      return { label: 'Upcoming', color: 'bg-blue-500/10 text-blue-500' };
    }
    if (isPast(endDate)) {
      return { label: 'Completed', color: 'bg-green-500/10 text-green-500' };
    }
    return { label: 'Active', color: 'bg-primary/10 text-primary' };
  };

  if (!activeWorkspaceId) {
    return <div className="p-8 text-center text-muted-foreground">Please select a workspace first.</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Programs</h1>
          <p className="text-muted-foreground mt-1">Manage hackathons, challenges, and incubations.</p>
        </div>
        <Button className="gap-2" onClick={() => setIsWizardOpen(true)}>
          <Plus className="h-4 w-4" />
          Create Program
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map(i => (
            <GlassPanel key={i} className="h-56 animate-pulse bg-secondary/20" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center p-8 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
          <p>{error.message}</p>
          <Button variant="outline" className="mt-4" onClick={fetchHackathons}>Try Again</Button>
        </div>
      ) : hackathons.length === 0 ? (
        <div className="text-center py-16">
          <div className="p-5 bg-primary/10 text-primary rounded-full w-20 h-20 mx-auto flex items-center justify-center mb-6">
            <Trophy className="h-10 w-10" />
          </div>
          <h2 className="text-2xl font-semibold mb-3">No programs found</h2>
          <p className="text-muted-foreground max-w-md mx-auto mb-8">
            Get started by creating your first hackathon, innovation challenge, or incubation program.
          </p>
          <Button size="lg" onClick={() => setIsWizardOpen(true)}>Create Your First Program</Button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {hackathons.map(hackathon => {
            const status = getStatusDisplay(hackathon);
            
            return (
              <GlassPanel 
                key={hackathon.id} 
                className="p-6 flex flex-col hover:border-primary/50 transition-all duration-300 cursor-pointer group hover:-translate-y-1 hover:shadow-xl hover:shadow-primary/10"
                onClick={() => navigate(`/hackathons/${hackathon.id}`)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1 pr-4">
                    <h3 className="text-lg font-semibold line-clamp-2 group-hover:text-primary transition-colors">
                      {hackathon.name}
                    </h3>
                  </div>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shrink-0 ${status.color}`}>
                    {status.label}
                  </span>
                </div>
                
                <p className="text-sm text-muted-foreground line-clamp-3 mb-6 flex-1">
                  {hackathon.description || 'No description provided.'}
                </p>
                
                <div className="space-y-3 mb-6 bg-secondary/10 p-3 rounded-lg border border-border/50">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4 text-primary/70" />
                    <span className="font-medium text-foreground">Start:</span>
                    <span>{format(new Date(hackathon.start_date), 'MMM d, yyyy')}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4 text-orange-500/70" />
                    <span className="font-medium text-foreground">End:</span>
                    <span>{format(new Date(hackathon.end_date), 'MMM d, yyyy')}</span>
                  </div>
                </div>
                
                <div className="mt-auto pt-4 border-t border-border/50 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                    <Activity className="h-3.5 w-3.5" />
                    <span className="uppercase tracking-wider">{hackathon.program_type || 'Hackathon'}</span>
                  </div>
                  <div className="flex items-center text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity transform group-hover:translate-x-0 -translate-x-2">
                    <span>Manage</span>
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </div>
                </div>
              </GlassPanel>
            );
          })}
        </div>
      )}

      <div className="mt-12">
        <ProgramSimulationEngine />
      </div>

      <ProgramCreationWizard 
        open={isWizardOpen} 
        onOpenChange={setIsWizardOpen} 
        onSuccess={fetchHackathons} 
      />
    </div>
  );
}
