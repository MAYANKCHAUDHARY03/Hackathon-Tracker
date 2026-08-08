import { useEffect, useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Webhook, Plus, Trash2, Activity } from 'lucide-react';
import { webhookApi, type WebhookSubscription, type WebhookDelivery } from '@/api/webhookApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

export function WebhookSettings() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [subscriptions, setSubscriptions] = useState<WebhookSubscription[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [newUrl, setNewUrl] = useState('');

  const fetchSubscriptions = async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    try {
      const data = await webhookApi.listSubscriptions(activeWorkspaceId);
      setSubscriptions(data);
    } catch (e) {
      toast.error('Failed to load webhook subscriptions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, [activeWorkspaceId]);

  const handleCreate = async () => {
    if (!activeWorkspaceId) return;
    try {
      await webhookApi.createSubscription(activeWorkspaceId, {
        url: newUrl,
        events: ['*'], // Default to all events
      });
      toast.success('Webhook created');
      setIsOpen(false);
      setNewUrl('');
      fetchSubscriptions();
    } catch (e) {
      toast.error('Failed to create webhook');
    }
  };

  return (
    <GlassPanel className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Webhook className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">Webhook Subscriptions</h2>
        </div>
        
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="gap-2">
              <Plus className="h-4 w-4" /> Add Webhook
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Webhook</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Payload URL</Label>
                <Input 
                  placeholder="https://example.com/webhook" 
                  value={newUrl} 
                  onChange={(e) => setNewUrl(e.target.value)} 
                />
              </div>
              <Button onClick={handleCreate} disabled={!newUrl} className="w-full">Create Webhook</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      
      <p className="text-sm text-muted-foreground">
        Set up webhooks to receive real-time HTTP payloads when events occur in this workspace.
      </p>
      
      <div className="space-y-3 pt-2">
        {loading ? (
          <div className="text-sm text-muted-foreground text-center py-4">Loading webhooks...</div>
        ) : subscriptions.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-8 border border-dashed border-border/50 rounded-lg bg-secondary/10">
            No webhooks configured. Add one to get started.
          </div>
        ) : (
          subscriptions.map((sub) => (
            <div key={sub.id} className="p-4 border border-border/50 rounded-lg bg-secondary/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <p className="font-medium text-sm flex items-center gap-2">
                  {sub.url}
                  <span className="px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 text-xs font-semibold">Active</span>
                </p>
                <p className="text-xs text-muted-foreground mt-1">Events: {sub.events.join(', ')}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-2">
                  <Activity className="h-4 w-4" /> Logs
                </Button>
                <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive hover:bg-destructive/10">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </GlassPanel>
  );
}
