import { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Trash2, Plus, Zap } from 'lucide-react';
import { format } from 'date-fns';

interface AutomationRule {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  trigger_config: Record<string, any>;
  action_type: string;
  action_config: Record<string, any>;
  is_active: boolean;
  created_at: string;
}

export function AutomationSettings() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [showForm, setShowForm] = useState(false);
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [triggerType, setTriggerType] = useState('submission_created');
  const [actionType, setActionType] = useState('send_notification');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeWorkspaceId) {
      loadRules();
    }
  }, [activeWorkspaceId]);

  async function loadRules() {
    try {
      const data = await apiClient.get<AutomationRule[]>(`/workspaces/${activeWorkspaceId}/automation/rules`);
      setRules(data);
    } catch (err) {
      console.error('Failed to load automation rules', err);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name || !triggerType || !actionType) return;
    setLoading(true);
    try {
      await apiClient.post(`/workspaces/${activeWorkspaceId}/automation/rules`, {
        name,
        description,
        trigger_type: triggerType,
        trigger_config: {},
        action_type: actionType,
        action_config: {},
        is_active: true
      });
      setShowForm(false);
      setName('');
      setDescription('');
      loadRules();
    } catch (err: any) {
      alert(err.data?.detail || 'Failed to create rule');
    } finally {
      setLoading(false);
    }
  }

  async function handleRemove(id: string) {
    if (!confirm('Remove this automation rule?')) return;
    try {
      await apiClient.delete(`/workspaces/${activeWorkspaceId}/automation/rules/${id}`);
      loadRules();
    } catch (err) {
      console.error(err);
      alert('Failed to remove rule');
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">Automate workflows in your workspace based on triggers.</p>
        <Button onClick={() => setShowForm(!showForm)} variant="outline" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Rule
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="p-4 bg-secondary/10 border border-border/50 rounded-lg space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Rule Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="E.g., Notify on new submission"
              className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Description</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          <div className="flex gap-4">
            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium">Trigger</label>
              <select
                value={triggerType}
                onChange={(e) => setTriggerType(e.target.value)}
                className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="submission_created">When a Submission is Created</option>
                <option value="task_completed">When a Task is Completed</option>
                <option value="schedule_daily">Daily Schedule</option>
              </select>
            </div>
            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium">Action</label>
              <select
                value={actionType}
                onChange={(e) => setActionType(e.target.value)}
                className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="send_notification">Send Notification</option>
                <option value="assign_evaluator">Assign Evaluator</option>
                <option value="move_task">Move Task to Next Column</option>
              </select>
            </div>
          </div>
          
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Rule'}
            </Button>
          </div>
        </form>
      )}

      {rules.length > 0 ? (
        <div className="space-y-3">
          {rules.map((rule) => (
            <div key={rule.id} className="flex items-center justify-between p-4 bg-secondary/20 border border-border/30 rounded-lg">
              <div>
                <p className="font-medium flex items-center gap-2">
                  <Zap className="h-4 w-4 text-yellow-500" />
                  {rule.name}
                  {rule.is_active && <span className="text-[10px] uppercase bg-green-500/20 text-green-500 px-2 py-0.5 rounded-full font-bold tracking-wider">Active</span>}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  When <strong>{rule.trigger_type.replace('_', ' ')}</strong>, then <strong>{rule.action_type.replace('_', ' ')}</strong>
                </p>
                <p className="text-xs text-muted-foreground mt-1 opacity-70">
                  Created {format(new Date(rule.created_at), 'PP')}
                </p>
              </div>
              <Button 
                variant="ghost" 
                size="icon"
                className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                onClick={() => handleRemove(rule.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      ) : (
        !showForm && (
          <div className="text-center p-8 border border-dashed border-border/50 rounded-lg text-muted-foreground">
            No automation rules configured yet.
          </div>
        )
      )}
    </div>
  );
}
