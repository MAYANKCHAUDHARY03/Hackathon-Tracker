import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { automationApi } from '@/api/automationApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { Loader2, Plus, Settings2, Trash2, Zap } from 'lucide-react';
import { format } from 'date-fns';

interface AutomationRuleListProps {
  onCreateClick: () => void;
  onEditClick: (ruleId: string) => void;
}

export function AutomationRuleList({ onCreateClick, onEditClick }: AutomationRuleListProps) {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const queryClient = useQueryClient();

  const { data: rules, isLoading } = useQuery({
    queryKey: ['automation-rules', workspaceId],
    queryFn: () => workspaceId ? automationApi.listRules(workspaceId) : Promise.resolve([]),
    enabled: !!workspaceId
  });

  const toggleRule = useMutation({
    mutationFn: ({ ruleId, enabled }: { ruleId: string; enabled: boolean }) => 
      automationApi.updateRule(workspaceId!, ruleId, { enabled }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-rules', workspaceId] });
      toast.success('Rule status updated');
    },
    onError: () => toast.error('Failed to update rule status')
  });

  const deleteRule = useMutation({
    mutationFn: (ruleId: string) => automationApi.deleteRule(workspaceId!, ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-rules', workspaceId] });
      toast.success('Rule deleted successfully');
    },
    onError: () => toast.error('Failed to delete rule')
  });

  if (!workspaceId) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            Automation Rules
          </h2>
          <p className="text-muted-foreground text-sm">Automate repetitive tasks and workflows.</p>
        </div>
        <Button onClick={onCreateClick}>
          <Plus className="w-4 h-4 mr-2" />
          Create Rule
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : rules?.length === 0 ? (
        <GlassPanel className="p-12 text-center flex flex-col items-center">
          <Settings2 className="w-12 h-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium">No Automation Rules</h3>
          <p className="text-muted-foreground mt-2 mb-6">Create your first rule to start automating your workspace.</p>
          <Button onClick={onCreateClick}>Create First Rule</Button>
        </GlassPanel>
      ) : (
        <div className="grid gap-4">
          {rules?.map((rule) => (
            <GlassPanel key={rule.id} className="p-6 flex flex-col md:flex-row gap-6 md:items-center justify-between hover-lift">
              <div className="flex-grow">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold">{rule.name}</h3>
                  <span className="text-xs px-2 py-1 rounded-full bg-secondary text-secondary-foreground font-medium">
                    {rule.trigger_type}
                  </span>
                </div>
                {rule.description && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{rule.description}</p>
                )}
                <div className="text-sm">
                  <span className="font-medium text-foreground">Action:</span> <span className="text-muted-foreground">{rule.action_type}</span>
                </div>
              </div>

              <div className="flex items-center gap-4 border-t md:border-t-0 md:border-l border-border pt-4 md:pt-0 md:pl-6">
                <div className="flex flex-col items-center gap-2">
                  <span className="text-xs text-muted-foreground font-medium">{rule.enabled ? 'Active' : 'Paused'}</span>
                  <Switch 
                    checked={rule.enabled ?? false} 
                    onCheckedChange={(checked) => toggleRule.mutate({ ruleId: rule.id, enabled: checked })}
                    disabled={toggleRule.isPending}
                  />
                </div>
                <div className="flex flex-col gap-2 ml-4">
                  <Button variant="outline" size="sm" onClick={() => onEditClick(rule.id)}>
                    Edit
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-destructive hover:bg-destructive/10"
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this rule?')) {
                        deleteRule.mutate(rule.id);
                      }
                    }}
                    disabled={deleteRule.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
