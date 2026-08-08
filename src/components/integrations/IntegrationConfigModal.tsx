import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { hubIntegrationApi, type ConnectorInfo } from '@/api/hubIntegrationApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { toast } from 'sonner';

interface IntegrationConfigModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  connector: ConnectorInfo;
  onSaved: () => void;
}

export function IntegrationConfigModal({ open, onOpenChange, connector, onSaved }: IntegrationConfigModalProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [name, setName] = useState('');
  const [config, setConfig] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!activeWorkspaceId) return;
    
    // Validate required fields
    for (const field of connector.config_schema.fields) {
      if (field.required && !config[field.id]) {
        toast.error(`Field ${field.label} is required`);
        return;
      }
    }

    setSaving(true);
    try {
      await hubIntegrationApi.createIntegration({
        workspace_id: activeWorkspaceId,
        connector_id: connector.id,
        name: name || `${connector.name} Integration`,
        is_active: true,
        config: config
      });
      toast.success('Integration created');
      onSaved();
    } catch (e) {
      console.error(e);
      toast.error('Failed to save integration');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Configure {connector.name}</DialogTitle>
          <DialogDescription>{connector.description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Connection Name</Label>
            <Input 
              value={name} 
              onChange={e => setName(e.target.value)} 
              placeholder="e.g. Engineering Slack" 
            />
          </div>

          {connector.config_schema.fields.map(field => (
            <div key={field.id} className="space-y-2">
              <Label>{field.label} {field.required && <span className="text-red-500">*</span>}</Label>
              <Input
                type={field.type === 'password' ? 'password' : 'text'}
                value={config[field.id] || ''}
                onChange={e => setConfig({ ...config, [field.id]: e.target.value })}
              />
            </div>
          ))}

          <Button className="w-full" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Integration'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
