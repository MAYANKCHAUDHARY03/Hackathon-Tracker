import { useState, useEffect } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Plug, Plus, CheckCircle, AlertTriangle, Play } from 'lucide-react';
import { hubIntegrationApi, type WorkspaceIntegration, type ConnectorInfo } from '@/api/hubIntegrationApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { toast } from 'sonner';
import { IntegrationConfigModal } from './IntegrationConfigModal';

export function IntegrationHub() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [integrations, setIntegrations] = useState<WorkspaceIntegration[]>([]);
  const [connectors, setConnectors] = useState<ConnectorInfo[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [selectedConnector, setSelectedConnector] = useState<ConnectorInfo | null>(null);
  
  const loadData = async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    try {
      const [ints, conns] = await Promise.all([
        hubIntegrationApi.getWorkspaceIntegrations(activeWorkspaceId),
        hubIntegrationApi.getConnectors()
      ]);
      setIntegrations(ints);
      setConnectors(conns);
    } catch (e) {
      console.error(e);
      toast.error('Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeWorkspaceId]);

  const handleTest = async (id: string) => {
    try {
      const res = await hubIntegrationApi.testIntegration(id);
      if (res.status === 'success') {
        toast.success('Integration test successful!');
      } else {
        toast.error(`Integration test failed: ${res.error}`);
      }
      loadData();
    } catch (e) {
      console.error(e);
      toast.error('Failed to test integration');
    }
  };

  if (!activeWorkspaceId) return null;

  return (
    <GlassPanel className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Plug className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">Enterprise Integrations</h2>
        </div>
      </div>
      
      <p className="text-sm text-muted-foreground mb-4">
        Connect Hackathon OS to your enterprise tools.
      </p>

      {/* Available Connectors */}
      <div className="space-y-2 mb-6">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Available Connectors</h3>
        <div className="flex gap-2 flex-wrap">
          {connectors.map(c => (
            <Button 
              key={c.id} 
              variant="outline" 
              className="gap-2" 
              onClick={() => {
                setSelectedConnector(c);
                setIsConfigModalOpen(true);
              }}
            >
              <Plus className="h-4 w-4" />
              {c.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Active Integrations */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Configured Integrations</h3>
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : integrations.length === 0 ? (
          <p className="text-sm text-muted-foreground">No integrations configured yet.</p>
        ) : (
          integrations.map(int => (
            <div key={int.id} className="p-4 border border-border/50 rounded-lg bg-secondary/20 flex justify-between items-center">
              <div>
                <p className="font-medium text-sm">{int.name} ({int.connector_id})</p>
                <div className="flex items-center gap-2 mt-1">
                  {int.last_sync_status === 'success' ? (
                    <CheckCircle className="h-3 w-3 text-green-500" />
                  ) : int.last_sync_status === 'error' ? (
                    <AlertTriangle className="h-3 w-3 text-red-500" />
                  ) : (
                    <div className="h-3 w-3 rounded-full bg-gray-500" />
                  )}
                  <span className="text-xs text-muted-foreground">
                    {int.last_sync_status ? `Last test: ${int.last_sync_status}` : 'Never tested'}
                  </span>
                </div>
              </div>
              <Button size="sm" variant="secondary" onClick={() => handleTest(int.id)}>
                <Play className="h-4 w-4 mr-2" />
                Test
              </Button>
            </div>
          ))
        )}
      </div>

      {selectedConnector && (
        <IntegrationConfigModal
          open={isConfigModalOpen}
          onOpenChange={setIsConfigModalOpen}
          connector={selectedConnector}
          onSaved={() => {
            setIsConfigModalOpen(false);
            loadData();
          }}
        />
      )}
    </GlassPanel>
  );
}
