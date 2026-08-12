import { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { teamApi } from '@/api/teamApi';
import type { Team } from '@/api/teamApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Users, Plus, Code, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function Teams() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [teams, setTeams] = useState<Team[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: '', description: '', skills_needed: '' });

  useEffect(() => {
    async function fetchTeams() {
      if (!activeWorkspaceId) return;
      setIsLoading(true);
      setError(null);
      try {
        const data = await teamApi.getTeams(activeWorkspaceId);
        setTeams(data);
      } catch (err: any) {
        setError(err instanceof Error ? err : new Error('Failed to load teams'));
      } finally {
        setIsLoading(false);
      }
    }
    fetchTeams();
  }, [activeWorkspaceId]);

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId) return;
    try {
      const created = await teamApi.createTeam(activeWorkspaceId, {
        name: newTeam.name,
        description: newTeam.description,
        skills_needed: newTeam.skills_needed.split(',').map(s => s.trim()).filter(Boolean),
        hackathon_id: 'default',
      });
      setTeams(prev => [...prev, created]);
      setIsDialogOpen(false);
      setNewTeam({ name: '', description: '', skills_needed: '' });
    } catch (err) {
      console.error(err);
    }
  };

  const handleApply = async (teamId: string) => {
    if (!activeWorkspaceId) return;
    try {
      await teamApi.applyToTeam(activeWorkspaceId, teamId);
      alert('Application sent successfully!');
    } catch (err) {
      alert('Failed to apply. You might already be applied or in a team.');
    }
  };

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team Database</h1>
          <p className="text-muted-foreground mt-1">Discover and join teams across the workspace.</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Create Team
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create a New Team</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateTeam} className="space-y-4 pt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Team Name</label>
                <input
                  required
                  type="text"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={newTeam.name}
                  onChange={e => setNewTeam({...newTeam, name: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <textarea
                  required
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={newTeam.description}
                  onChange={e => setNewTeam({...newTeam, description: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Skills Needed (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g. React, Python, Design"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={newTeam.skills_needed}
                  onChange={e => setNewTeam({...newTeam, skills_needed: e.target.value})}
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit">Create Team</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map(i => (
            <GlassPanel key={i} className="h-48 animate-pulse bg-secondary/20" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center p-8 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
          <p>{error.message}</p>
        </div>
      ) : teams.length === 0 ? (
        <div className="text-center py-12">
          <div className="p-4 bg-primary/10 text-primary rounded-full w-16 h-16 mx-auto flex items-center justify-center mb-4">
            <Users className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-semibold mb-2">No teams found</h2>
          <p className="text-muted-foreground max-w-md mx-auto mb-6">
            There are no teams in this workspace yet. Be the first to create one!
          </p>
          <Button onClick={() => setIsDialogOpen(true)}>Create Team</Button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {teams.map(team => (
            <GlassPanel key={team.id} className="p-6 flex flex-col hover:border-primary/30 transition-colors">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold truncate pr-4">{team.name}</h3>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-primary/10 text-primary px-2 py-1 rounded">
                  {team.status}
                </span>
              </div>
              
              <p className="text-sm text-muted-foreground line-clamp-2 mb-4 flex-1">
                {team.description || 'No description provided.'}
              </p>
              
              <div className="space-y-3 mb-6">
                {team.skills_needed && team.skills_needed.length > 0 && (
                  <div className="flex items-start gap-2 text-sm text-muted-foreground">
                    <Code className="h-4 w-4 mt-0.5 shrink-0" />
                    <div className="flex flex-wrap gap-1">
                      {team.skills_needed.map((skill, i) => (
                        <span key={i} className="bg-secondary/50 px-1.5 py-0.5 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Created {format(new Date(team.created_at), 'MMM d, yyyy')}</span>
                </div>
              </div>
              
              <div className="mt-auto pt-4 border-t border-border/50 flex gap-2">
                <Button 
                  className="flex-1" 
                  onClick={() => handleApply(team.id)}
                >
                  Apply
                </Button>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
