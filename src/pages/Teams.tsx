import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { teamApi, type Team } from '@/api/teamApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Users, Plus, Loader2, UserPlus, Search } from 'lucide-react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';

export default function Teams() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Form State
  const [name, setName] = useState('');
  const [hackathonId, setHackathonId] = useState('');
  const [description, setDescription] = useState('');
  const [skills, setSkills] = useState('');

  const { data: teams, isLoading } = useQuery({
    queryKey: ['teams', activeWorkspaceId],
    queryFn: () => teamApi.getTeams(activeWorkspaceId!),
    enabled: !!activeWorkspaceId
  });

  const createTeam = useMutation({
    mutationFn: (data: Partial<Team>) => teamApi.createTeam(activeWorkspaceId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', activeWorkspaceId] });
      toast.success('Team created successfully!');
      setIsDialogOpen(false);
      setName('');
      setHackathonId('');
      setDescription('');
      setSkills('');
    },
    onError: () => toast.error('Failed to create team')
  });

  const applyToTeam = useMutation({
    mutationFn: (teamId: string) => teamApi.applyToTeam(activeWorkspaceId!, teamId),
    onSuccess: () => toast.success('Application sent!'),
    onError: () => toast.error('Failed to apply to team')
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const skillsList = skills.split(',').map(s => s.trim()).filter(Boolean);
    createTeam.mutate({
      name,
      hackathon_id: hackathonId,
      description,
      skills_needed: skillsList,
      status: 'forming'
    });
  };

  const filteredTeams = teams?.filter(team => 
    team.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    team.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!activeWorkspaceId) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-muted-foreground">
        Please select a workspace to view teams.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Users className="w-8 h-8 text-primary" />
            Team Database
          </h1>
          <p className="text-muted-foreground text-lg mt-1">
            Browse and manage all hackathon teams in your workspace.
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Team
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create a New Team</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Team Name</Label>
                <Input value={name} onChange={e => setName(e.target.value)} required placeholder="e.g. Byte Builders" />
              </div>
              <div className="space-y-2">
                <Label>Hackathon ID</Label>
                <Input value={hackathonId} onChange={e => setHackathonId(e.target.value)} required placeholder="Which hackathon?" />
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea 
                  value={description} 
                  onChange={e => setDescription(e.target.value)} 
                  placeholder="What is your team building?" 
                />
              </div>
              <div className="space-y-2">
                <Label>Skills Needed</Label>
                <Input 
                  value={skills} 
                  onChange={e => setSkills(e.target.value)} 
                  placeholder="React, Python, Design (comma separated)" 
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={createTeam.isPending || !name || !hackathonId}>
                  {createTeam.isPending ? 'Creating...' : 'Create Team'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input 
          placeholder="Search teams..." 
          className="pl-9"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : filteredTeams?.length === 0 ? (
        <GlassPanel className="p-12 text-center flex flex-col items-center">
          <Users className="w-12 h-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium">No Teams Found</h3>
          <p className="text-muted-foreground mt-2">
            Try adjusting your search or create a new team to get started.
          </p>
        </GlassPanel>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTeams?.map(team => (
            <GlassPanel key={team.id} className="p-6 flex flex-col h-full hover:bg-secondary/20 transition-colors group">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-bold text-xl">{team.name}</h3>
                  <div className="text-xs font-medium uppercase tracking-wider text-primary mt-1">
                    {team.status}
                  </div>
                </div>
                <div className="bg-secondary/50 p-2 rounded-full text-muted-foreground">
                  <Users className="w-5 h-5" />
                </div>
              </div>
              
              <p className="text-sm text-muted-foreground line-clamp-3 mb-6 flex-1">
                {team.description || 'No description provided.'}
              </p>

              {team.skills_needed && team.skills_needed.length > 0 && (
                <div className="mb-6">
                  <div className="text-xs font-medium text-foreground mb-2">Skills Needed:</div>
                  <div className="flex flex-wrap gap-2">
                    {team.skills_needed.map((skill, idx) => (
                      <span key={idx} className="bg-secondary px-2 py-1 rounded text-xs">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-4 border-t border-border/50">
                <Button 
                  className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
                  variant="secondary"
                  onClick={() => applyToTeam.mutate(team.id)}
                  disabled={applyToTeam.isPending}
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Apply to Join
                </Button>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
