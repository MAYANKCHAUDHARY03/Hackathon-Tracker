import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { developerApi, type DeveloperApp, type DeveloperAppCreate } from '@/api/developerApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Terminal, Plus, Key, Link as LinkIcon, Loader2, Copy } from 'lucide-react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { format } from 'date-fns';

export default function DeveloperPortal() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [appName, setAppName] = useState('');
  const [redirectUris, setRedirectUris] = useState('');

  const { data: apps, isLoading } = useQuery({
    queryKey: ['developer-apps', activeWorkspaceId],
    queryFn: () => developerApi.getApps(activeWorkspaceId!),
    enabled: !!activeWorkspaceId
  });

  const createApp = useMutation({
    mutationFn: (data: DeveloperAppCreate) => developerApi.createApp(activeWorkspaceId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['developer-apps', activeWorkspaceId] });
      toast.success('Developer app created');
      setIsDialogOpen(false);
      setAppName('');
      setRedirectUris('');
    },
    onError: () => toast.error('Failed to create developer app')
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const uris = redirectUris.split(',').map(uri => uri.trim()).filter(Boolean);
    createApp.mutate({
      name: appName,
      redirect_uris: uris
    });
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  if (!activeWorkspaceId) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-muted-foreground">
        Please select a workspace to manage developer apps.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Terminal className="w-8 h-8 text-primary" />
            Developer Portal
          </h1>
          <p className="text-muted-foreground text-lg mt-1">
            Manage OAuth applications and API clients for this workspace.
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Register App
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Register New Application</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>App Name</Label>
                <Input 
                  value={appName} 
                  onChange={e => setAppName(e.target.value)} 
                  required 
                  placeholder="My Cool App" 
                />
              </div>
              <div className="space-y-2">
                <Label>Redirect URIs</Label>
                <Input 
                  value={redirectUris} 
                  onChange={e => setRedirectUris(e.target.value)} 
                  required 
                  placeholder="https://app.example.com/oauth/callback (comma separated)" 
                />
                <p className="text-xs text-muted-foreground">
                  Separate multiple URIs with commas.
                </p>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={createApp.isPending || !appName || !redirectUris}>
                  {createApp.isPending ? 'Registering...' : 'Register App'}
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
      ) : apps?.length === 0 ? (
        <GlassPanel className="p-12 text-center flex flex-col items-center">
          <Terminal className="w-12 h-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium">No Apps Registered</h3>
          <p className="text-muted-foreground mt-2">
            Create an OAuth application to integrate your custom tools with the HackTracker API.
          </p>
        </GlassPanel>
      ) : (
        <div className="grid gap-6">
          {apps?.map(app => (
            <GlassPanel key={app.id} className="p-6">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                <div className="space-y-4 flex-1">
                  <div>
                    <h3 className="text-xl font-bold">{app.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      Created {format(new Date(app.created_at), 'PPP')}
                    </p>
                  </div>
                  
                  <div className="space-y-3 bg-background/50 p-4 rounded-lg border border-border/50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Key className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Client ID</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <code className="text-xs bg-secondary px-2 py-1 rounded">{app.client_id}</code>
                        <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => copyToClipboard(app.client_id, 'Client ID')}>
                          <Copy className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Key className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Client Secret</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <code className="text-xs bg-secondary px-2 py-1 rounded select-all blur-[4px] hover:blur-none transition-all">
                          {app.client_secret}
                        </code>
                        <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => copyToClipboard(app.client_secret, 'Client Secret')}>
                          <Copy className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex-1 space-y-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                    <LinkIcon className="w-4 h-4 text-muted-foreground" />
                    Authorized Redirect URIs
                  </div>
                  <div className="space-y-2">
                    {app.redirect_uris.map((uri, idx) => (
                      <div key={idx} className="text-sm bg-secondary/50 p-2 rounded truncate border border-border/50" title={uri}>
                        {uri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
