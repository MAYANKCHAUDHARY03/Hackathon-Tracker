import { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { LinkIcon, Trash2, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';

interface Connection {
  id: string;
  provider_name: string;
  is_active: boolean;
  last_sync_at: string | null;
}

export function IntegrationSettings() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [provider, setProvider] = useState('devfolio');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [syncingId, setSyncingId] = useState<string | null>(null);

  useEffect(() => {
    if (activeWorkspaceId) {
      loadConnections();
    }
  }, [activeWorkspaceId]);

  async function loadConnections() {
    try {
      const data = await apiClient.get<Connection[]>(`/workspaces/${activeWorkspaceId}/integrations/connections`);
      setConnections(data);
    } catch (err) {
      console.error('Failed to load connections', err);
    }
  }

  async function handleConnect(e: React.FormEvent) {
    e.preventDefault();
    if (!apiKey) return;
    setLoading(true);
    try {
      await apiClient.post(`/workspaces/${activeWorkspaceId}/integrations/connections`, {
        provider_name: provider,
        credentials: { api_key: apiKey },
        is_active: true
      });
      setApiKey('');
      loadConnections();
    } catch (err: any) {
      alert(err.data?.detail || 'Failed to connect');
    } finally {
      setLoading(false);
    }
  }

  async function handleRemove(id: string) {
    if (!confirm('Remove this integration?')) return;
    try {
      await apiClient.delete(`/workspaces/${activeWorkspaceId}/integrations/connections/${id}`);
      loadConnections();
    } catch (err) {
      console.error(err);
      alert('Failed to remove connection');
    }
  }

  async function handleSync(id: string) {
    setSyncingId(id);
    try {
      // Dummy hackathon reference for now, ideally selected from UI
      await apiClient.post(`/workspaces/${activeWorkspaceId}/integrations/connections/${id}/sync`, {
        hackathon_reference: 'dummy_ref'
      });
      alert('Sync successful');
      loadConnections();
    } catch (err: any) {
      alert(err.data?.detail || 'Sync failed');
    } finally {
      setSyncingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleConnect} className="flex gap-4 items-end">
        <div className="w-48 space-y-2">
          <label className="text-sm font-medium">Provider</label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="devfolio">Devfolio</option>
            <option value="unstop">Unstop</option>
          </select>
        </div>
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium">API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter API token..."
            className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>
        <Button type="submit" disabled={loading} className="h-10">
          <LinkIcon className="h-4 w-4 mr-2" />
          {loading ? 'Connecting...' : 'Connect'}
        </Button>
      </form>

      {connections.length > 0 && (
        <div className="space-y-3 pt-4 border-t border-border/50">
          <h3 className="text-sm font-medium text-muted-foreground">Active Connections</h3>
          {connections.map((conn) => (
            <div key={conn.id} className="flex items-center justify-between p-4 bg-secondary/20 border border-border/30 rounded-lg">
              <div>
                <p className="font-medium capitalize flex items-center gap-2">
                  {conn.provider_name}
                  {conn.is_active && <span className="w-2 h-2 rounded-full bg-green-500" title="Active"></span>}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Last sync: {conn.last_sync_at ? format(new Date(conn.last_sync_at), 'PP p') : 'Never'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleSync(conn.id)}
                  disabled={syncingId === conn.id}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${syncingId === conn.id ? 'animate-spin' : ''}`} />
                  Sync
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                  onClick={() => handleRemove(conn.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
