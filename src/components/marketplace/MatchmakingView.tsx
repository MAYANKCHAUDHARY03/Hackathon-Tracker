import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { matchmakingApi, type MatchProfileCreate, type MatchOpportunityCreate } from '@/api/matchmakingApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Loader2, Plus, Sparkles, TrendingUp, Handshake } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';

export function MatchmakingView() {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const queryClient = useQueryClient();
  
  // Create Profile state
  const [profileOpen, setProfileOpen] = useState(false);
  const [entityType, setEntityType] = useState('project');
  const [entityId, setEntityId] = useState('');
  const [lookingFor, setLookingFor] = useState('');
  const [profileTags, setProfileTags] = useState('');

  // Create Opportunity state
  const [oppOpen, setOppOpen] = useState(false);
  const [oppType, setOppType] = useState('investor');
  const [oppTitle, setOppTitle] = useState('');
  const [oppDescription, setOppDescription] = useState('');
  const [oppTags, setOppTags] = useState('');

  // State to simulate having a profile and generating recommendations
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);

  const { data: opportunities, isLoading: oppsLoading } = useQuery({
    queryKey: ['matchmaking-opportunities', workspaceId],
    queryFn: () => workspaceId ? matchmakingApi.listOpportunities(workspaceId) : Promise.resolve([]),
    enabled: !!workspaceId
  });

  const { data: recommendations, isLoading: recsLoading, refetch: refetchRecs } = useQuery({
    queryKey: ['matchmaking-recommendations', workspaceId, activeProfileId],
    queryFn: () => (workspaceId && activeProfileId) ? matchmakingApi.generateRecommendations(workspaceId, activeProfileId) : Promise.resolve([]),
    enabled: !!workspaceId && !!activeProfileId
  });

  const createProfile = useMutation({
    mutationFn: (data: MatchProfileCreate) => matchmakingApi.createProfile(workspaceId!, data),
    onSuccess: (data) => {
      toast.success('Match profile created successfully!');
      setActiveProfileId(data.id);
      setProfileOpen(false);
    },
    onError: () => toast.error('Failed to create match profile')
  });

  const createOpp = useMutation({
    mutationFn: (data: MatchOpportunityCreate) => matchmakingApi.createOpportunity(workspaceId!, data),
    onSuccess: () => {
      toast.success('Opportunity created successfully!');
      queryClient.invalidateQueries({ queryKey: ['matchmaking-opportunities', workspaceId] });
      setOppOpen(false);
      setOppTitle('');
      setOppDescription('');
      setOppTags('');
    },
    onError: () => toast.error('Failed to create opportunity')
  });

  const handleCreateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    if (!entityId) return;
    createProfile.mutate({
      entity_type: entityType,
      entity_id: entityId,
      looking_for: lookingFor.split(',').map(s => s.trim()).filter(Boolean),
      tags: profileTags.split(',').map(s => s.trim()).filter(Boolean)
    });
  };

  const handleCreateOpp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!oppTitle) return;
    createOpp.mutate({
      type: oppType,
      title: oppTitle,
      description: oppDescription,
      tags: oppTags.split(',').map(s => s.trim()).filter(Boolean)
    });
  };

  if (!workspaceId) return null;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Handshake className="w-6 h-6 text-primary" />
            Ecosystem Matchmaking
          </h2>
          <p className="text-muted-foreground mt-1">Connect startups with investors, mentors, and grants.</p>
        </div>
        
        <div className="flex gap-4">
          <Dialog open={profileOpen} onOpenChange={setProfileOpen}>
            <DialogTrigger asChild>
              <Button variant="outline"><Plus className="w-4 h-4 mr-2" /> Create Match Profile</Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateProfile}>
                <DialogHeader>
                  <DialogTitle>Create Match Profile</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>Entity Type</Label>
                    <Select value={entityType} onValueChange={setEntityType}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="project">Project</SelectItem>
                        <SelectItem value="startup">Startup</SelectItem>
                        <SelectItem value="team">Team</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Entity ID (UUID)</Label>
                    <Input value={entityId} onChange={e => setEntityId(e.target.value)} placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000" required />
                  </div>
                  <div className="space-y-2">
                    <Label>Looking For (Comma separated)</Label>
                    <Input value={lookingFor} onChange={e => setLookingFor(e.target.value)} placeholder="e.g. mentor, seed-funding, azure-credits" />
                  </div>
                  <div className="space-y-2">
                    <Label>Profile Tags (Comma separated)</Label>
                    <Input value={profileTags} onChange={e => setProfileTags(e.target.value)} placeholder="e.g. fintech, ai, early-stage" />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="ghost" onClick={() => setProfileOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={createProfile.isPending}>
                    {createProfile.isPending ? 'Creating...' : 'Create Profile'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={oppOpen} onOpenChange={setOppOpen}>
            <DialogTrigger asChild>
              <Button><Plus className="w-4 h-4 mr-2" /> Post Opportunity</Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateOpp}>
                <DialogHeader>
                  <DialogTitle>Post Match Opportunity</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>Opportunity Type</Label>
                    <Select value={oppType} onValueChange={setOppType}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="investor">Investor Funding</SelectItem>
                        <SelectItem value="grant">Grant / Credits</SelectItem>
                        <SelectItem value="mentor">Mentorship</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Title</Label>
                    <Input value={oppTitle} onChange={e => setOppTitle(e.target.value)} placeholder="e.g. $100k Seed Fund for AI Startups" required />
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Textarea value={oppDescription} onChange={e => setOppDescription(e.target.value)} placeholder="Details about this opportunity..." />
                  </div>
                  <div className="space-y-2">
                    <Label>Opportunity Tags (Comma separated)</Label>
                    <Input value={oppTags} onChange={e => setOppTags(e.target.value)} placeholder="e.g. ai, seed-funding, startup" />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="ghost" onClick={() => setOppOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={createOpp.isPending}>
                    {createOpp.isPending ? 'Posting...' : 'Post Opportunity'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recommendations Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              Your Recommendations
            </h3>
            {activeProfileId && (
              <Button variant="ghost" size="sm" onClick={() => refetchRecs()}>
                Refresh
              </Button>
            )}
          </div>
          
          <GlassPanel className="p-6">
            {!activeProfileId ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">Create a match profile to see AI-generated recommendations.</p>
                <Button variant="outline" onClick={() => setProfileOpen(true)}>Create Profile</Button>
              </div>
            ) : recsLoading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : recommendations?.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No strong matches found at this time.
              </div>
            ) : (
              <div className="space-y-4">
                {recommendations?.map(rec => (
                  <div key={rec.id} className="p-4 rounded-xl border border-border bg-card/50 hover:bg-card transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-lg">{rec.opportunity.title}</h4>
                      <Badge variant={rec.score > 70 ? 'default' : 'secondary'}>
                        {Math.round(rec.score)}% Match
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{rec.opportunity.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {rec.opportunity.tags.map(t => (
                        <span key={t} className="text-xs bg-secondary px-2 py-1 rounded-md">{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </GlassPanel>
        </div>

        {/* Opportunities List Section */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            Active Opportunities
          </h3>
          
          <GlassPanel className="p-6">
            {oppsLoading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : opportunities?.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No opportunities posted yet.
              </div>
            ) : (
              <div className="space-y-4">
                {opportunities?.map(opp => (
                  <div key={opp.id} className="p-4 rounded-xl border border-border bg-card/50 hover:bg-card transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-lg">{opp.title}</h4>
                        <span className="text-xs text-muted-foreground capitalize">{opp.type}</span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{opp.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {opp.tags.map(t => (
                        <span key={t} className="text-xs bg-secondary/50 border border-border/50 px-2 py-1 rounded-md">{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </GlassPanel>
        </div>
      </div>
    </div>
  );
}
