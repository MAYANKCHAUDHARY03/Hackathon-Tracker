import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { hubIntegrationApi, type ConnectorInfo, type WorkspaceIntegration } from '@/api/hubIntegrationApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Network, Plus, CheckCircle2, XCircle, Loader2, Play } from 'lucide-react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';

export default function HubIntegration() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const queryClient = useQueryClient();
  const [selectedConnector, setSelectedConnector] = useState<ConnectorInfo | null>(null);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [integrationName, setIntegrationName] = useState('');
  const [configValues, setConfigValues] = useState<Record<string, string>>({});

  const { data: connectors, isLoading: loadingConnectors } = useQuery({
    queryKey: ['hub-connectors'],
    queryFn: hubIntegrationApi.getConnectors,
  });

  const { data: integrations, isLoading: loadingIntegrations } = useQuery({
    queryKey: ['hub-integrations', activeWorkspaceId],
    queryFn: () => hubIntegrationApi.getWorkspaceIntegrations(activeWorkspaceId!),
    enabled: !!activeWorkspaceId
  });

  const createIntegration = useMutation({
    mutationFn: (data: { workspace_id: string; connector_id: string; name: string; is_active: boolean; config: Record<string, any> }) => 
      hubIntegrationApi.createIntegration(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hub-integrations', activeWorkspaceId] });
      toast.success('Integration created');
      setIsConfigOpen(false);
      setSelectedConnector(null);
      setIntegrationName('');
      setConfigValues({});
    },
    onError: () => toast.error('Failed to create integration')
  });

  const testIntegration = useMutation({
    mutationFn: hubIntegrationApi.testIntegration,
    onSuccess: (res) => {
      if (res.status === 'success') {
        toast.success('Integration test successful!');
      } else {
        toast.error(`Integration test failed: ${res.error}`);
      }
      queryClient.invalidateQueries({ queryKey: ['hub-integrations', activeWorkspaceId] });
    },
    onError: () => toast.error('Error occurred while testing integration')
  });

  const handleConfigure = (connector: ConnectorInfo) => {
    setSelectedConnector(connector);
    setIntegrationName(connector.name);
    setConfigValues({});
    setIsConfigOpen(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConnector || !activeWorkspaceId) return;

    createIntegration.mutate({
      workspace_id: activeWorkspaceId,
      connector_id: selectedConnector.id,
      name: integrationName,
      is_active: true,
      config: configValues
    });
  };

  if (!activeWorkspaceId) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-muted-foreground">
        Please select a workspace to manage integrations.
      </div>
    );
  }

  const isLoading = loadingConnectors || loadingIntegrations;

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto p-4 md:p-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Network className="w-8 h-8 text-primary" />
          Hub Integrations
        </h1>
        <p className="text-muted-foreground text-lg mt-1">
          Connect HackTracker with your favorite external tools and services.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="space-y-12">
          {/* Active Integrations Section */}
          <section>
            <h2 className="text-xl font-semibold mb-4 border-b border-border/50 pb-2">Active Integrations</h2>
            {integrations?.length === 0 ? (
              <GlassPanel className="p-8 text-center text-muted-foreground">
                No active integrations. Browse the catalog below to connect a service.
              </GlassPanel>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {integrations?.map(integration => {
                  const connector = connectors?.find(c => c.id === integration.connector_id);
                  return (
                    <GlassPanel key={integration.id} className="p-6 flex flex-col h-full">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-bold text-lg">{integration.name}</h3>
                          <p className="text-sm text-muted-foreground">{connector?.name || integration.connector_id}</p>
                        </div>
                        {integration.is_active ? (
                          <div className="flex items-center gap-1 text-xs font-medium text-green-500 bg-green-500/10 px-2 py-1 rounded">
                            <CheckCircle2 className="w-3 h-3" /> Active
                          </div>
                        ) : (
                          <div className="flex items-center gap-1 text-xs font-medium text-red-500 bg-red-500/10 px-2 py-1 rounded">
                            <XCircle className="w-3 h-3" /> Inactive
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-auto space-y-4 pt-4 border-t border-border/50">
                        <div className="text-sm">
                          <div className="text-muted-foreground mb-1 text-xs uppercase tracking-wider">Status</div>
                          {integration.last_sync_status === 'success' ? (
                            <span className="text-green-500 flex items-center gap-1"><CheckCircle2 className="w-4 h-4"/> Sync Ok</span>
                          ) : integration.last_sync_status === 'error' ? (
                            <span className="text-red-500 flex items-center gap-1" title={integration.last_sync_error || ''}><XCircle className="w-4 h-4"/> Error</span>
                          ) : (
                            <span className="text-muted-foreground">Never tested</span>
                          )}
                        </div>
                        <Button 
                          variant="secondary" 
                          size="sm" 
                          className="w-full"
                          onClick={() => testIntegration.mutate(integration.id)}
                          disabled={testIntegration.isPending}
                        >
                          <Play className="w-4 h-4 mr-2" />
                          Test Connection
                        </Button>
                      </div>
                    </GlassPanel>
                  );
                })}
              </div>
            )}
          </section>

          {/* Connector Catalog Section */}
          <section>
            <h2 className="text-xl font-semibold mb-4 border-b border-border/50 pb-2">Connector Catalog</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {connectors?.map(connector => (
                <GlassPanel key={connector.id} className="p-6 flex flex-col h-full hover:bg-secondary/20 transition-colors">
                  <div className="mb-4">
                    <div className="text-xs font-bold uppercase tracking-wider text-primary mb-2">
                      {connector.category}
                    </div>
                    <h3 className="font-bold text-lg leading-tight mb-2">{connector.name}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {connector.description}
                    </p>
                  </div>
                  <div className="mt-auto pt-4 border-t border-border/50">
                    <Button 
                      className="w-full" 
                      onClick={() => handleConfigure(connector)}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  </div>
                </GlassPanel>
              ))}
            </div>
          </section>
        </div>
      )}

      {/* Configuration Dialog */}
      <Dialog open={isConfigOpen} onOpenChange={setIsConfigOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Configure {selectedConnector?.name}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label>Integration Name</Label>
              <Input 
                value={integrationName} 
                onChange={e => setIntegrationName(e.target.value)} 
                required 
                placeholder="My Slack Workspace" 
              />
            </div>
            
            {selectedConnector?.config_schema.fields.map(field => (
              <div key={field.id} className="space-y-2">
                <Label>
                  {field.label} {field.required && <span className="text-destructive">*</span>}
                </Label>
                <Input
                  type={field.type === 'password' || field.type === 'secret' ? 'password' : 'text'}
                  value={configValues[field.id] || ''}
                  onChange={e => setConfigValues(prev => ({ ...prev, [field.id]: e.target.value }))}
                  required={field.required}
                />
              </div>
            ))}
            
            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="ghost" onClick={() => setIsConfigOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={createIntegration.isPending || !integrationName}>
                {createIntegration.isPending ? 'Saving...' : 'Connect'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
