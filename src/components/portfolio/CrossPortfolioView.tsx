import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { crossPortfolioApi, type PortfolioCreate, type PortfolioProjectAdd } from '@/api/crossPortfolioApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Loader2, Plus, Briefcase, PlusCircle, LayoutGrid } from 'lucide-react';
import { format } from 'date-fns';

export function CrossPortfolioView() {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const queryClient = useQueryClient();
  
  const [createOpen, setCreateOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  
  const [linkOpen, setLinkOpen] = useState<string | null>(null); // portfolio ID
  const [projectIdToLink, setProjectIdToLink] = useState('');

  const { data: portfolios, isLoading } = useQuery({
    queryKey: ['cross-portfolios', workspaceId],
    queryFn: () => workspaceId ? crossPortfolioApi.listPortfolios(workspaceId) : Promise.resolve([]),
    enabled: !!workspaceId
  });

  const createPortfolio = useMutation({
    mutationFn: (data: PortfolioCreate) => crossPortfolioApi.createPortfolio(workspaceId!, data),
    onSuccess: () => {
      toast.success('Portfolio created successfully!');
      queryClient.invalidateQueries({ queryKey: ['cross-portfolios', workspaceId] });
      setCreateOpen(false);
      setName('');
      setDescription('');
    },
    onError: () => toast.error('Failed to create portfolio')
  });

  const linkProject = useMutation({
    mutationFn: ({ portfolioId, data }: { portfolioId: string, data: PortfolioProjectAdd }) => 
      crossPortfolioApi.addProjectToPortfolio(workspaceId!, portfolioId, data),
    onSuccess: () => {
      toast.success('Project linked to portfolio!');
      queryClient.invalidateQueries({ queryKey: ['cross-portfolios', workspaceId] });
      setLinkOpen(null);
      setProjectIdToLink('');
    },
    onError: () => toast.error('Failed to link project')
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    createPortfolio.mutate({
      name,
      description,
      is_public: true
    });
  };

  const handleLink = (e: React.FormEvent, portfolioId: string) => {
    e.preventDefault();
    if (!projectIdToLink) return;
    linkProject.mutate({
      portfolioId,
      data: { project_id: projectIdToLink }
    });
  };

  if (!workspaceId) return null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <LayoutGrid className="w-5 h-5 text-primary" />
            Cross-Hackathon Portfolios
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">Organize and showcase your projects across different hackathons.</p>
        </div>
        
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button variant="outline"><Plus className="w-4 h-4 mr-2" /> New Portfolio</Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle>Create Cross-Hackathon Portfolio</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>Portfolio Name</Label>
                  <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. My Web3 Ventures" required />
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="A short description of this portfolio's focus..." />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="ghost" onClick={() => setCreateOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={createPortfolio.isPending || !name}>
                  {createPortfolio.isPending ? 'Creating...' : 'Create Portfolio'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : portfolios?.length === 0 ? (
        <GlassPanel className="p-12 text-center">
          <Briefcase className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground">No Portfolios Found</h3>
          <p className="text-muted-foreground mt-2 mb-4">You haven't created any cross-hackathon portfolios yet.</p>
          <Button onClick={() => setCreateOpen(true)}>Create Your First Portfolio</Button>
        </GlassPanel>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {portfolios?.map(portfolio => (
            <GlassPanel key={portfolio.id} className="p-6 flex flex-col hover-lift bg-card/50">
              <div className="flex-grow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-lg">{portfolio.name}</h3>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(portfolio.created_at), 'MMM d, yyyy')}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {portfolio.description || 'No description provided.'}
                </p>
                
                <div className="text-sm font-medium mb-2">Projects ({portfolio.projects?.length || 0})</div>
                {portfolio.projects && portfolio.projects.length > 0 ? (
                  <ul className="space-y-1 mb-4">
                    {portfolio.projects.map((proj: any) => (
                      <li key={proj.id} className="text-xs px-2 py-1 bg-secondary rounded truncate">
                        {proj.name || proj.title || proj.id}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-muted-foreground italic mb-4">No projects linked yet.</p>
                )}
              </div>
              
              <div className="pt-4 border-t border-border mt-auto">
                <Dialog open={linkOpen === portfolio.id} onOpenChange={(open) => setLinkOpen(open ? portfolio.id : null)}>
                  <DialogTrigger asChild>
                    <Button variant="secondary" size="sm" className="w-full">
                      <PlusCircle className="w-4 h-4 mr-2" /> Link Project
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <form onSubmit={(e) => handleLink(e, portfolio.id)}>
                      <DialogHeader>
                        <DialogTitle>Link Project to {portfolio.name}</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label>Project ID (UUID)</Label>
                          <Input value={projectIdToLink} onChange={e => setProjectIdToLink(e.target.value)} placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000" required />
                        </div>
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button type="button" variant="ghost" onClick={() => setLinkOpen(null)}>Cancel</Button>
                        <Button type="submit" disabled={linkProject.isPending || !projectIdToLink}>
                          {linkProject.isPending ? 'Linking...' : 'Link Project'}
                        </Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
