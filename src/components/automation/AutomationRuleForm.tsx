import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { automationApi, type AutomationRuleCreate, type AutomationRuleUpdate } from '@/api/automationApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { toast } from 'sonner';

interface AutomationRuleFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  ruleId?: string | null;
}

const TRIGGER_OPTIONS = [
  { value: 'project_created', label: 'Project Created' },
  { value: 'project_submitted', label: 'Project Submitted' },
  { value: 'team_formed', label: 'Team Formed' },
  { value: 'user_joined', label: 'User Joined Workspace' },
];

const ACTION_OPTIONS = [
  { value: 'send_email', label: 'Send Email' },
  { value: 'create_notification', label: 'Create Notification' },
  { value: 'assign_tag', label: 'Assign Tag' },
  { value: 'webhook', label: 'Trigger Webhook' },
];

export function AutomationRuleForm({ open, onOpenChange, ruleId }: AutomationRuleFormProps) {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const queryClient = useQueryClient();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [triggerType, setTriggerType] = useState('');
  const [actionType, setActionType] = useState('');
  const [conditionsString, setConditionsString] = useState('{}');

  const { data: existingRule } = useQuery({
    queryKey: ['automation-rule', workspaceId, ruleId],
    queryFn: () => automationApi.getRule(workspaceId!, ruleId!),
    enabled: !!workspaceId && !!ruleId && open
  });

  useEffect(() => {
    if (existingRule && ruleId) {
      setName(existingRule.name);
      setDescription(existingRule.description || '');
      setTriggerType(existingRule.trigger_type);
      setActionType(existingRule.action_type);
      setConditionsString(JSON.stringify(existingRule.conditions, null, 2));
    } else if (!ruleId && open) {
      setName('');
      setDescription('');
      setTriggerType('');
      setActionType('');
      setConditionsString('{\n  \n}');
    }
  }, [existingRule, ruleId, open]);

  const saveRule = useMutation({
    mutationFn: (data: any) => {
      if (ruleId) {
        return automationApi.updateRule(workspaceId!, ruleId, data as AutomationRuleUpdate);
      } else {
        return automationApi.createRule(workspaceId!, data as AutomationRuleCreate);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-rules', workspaceId] });
      toast.success(`Rule ${ruleId ? 'updated' : 'created'} successfully`);
      onOpenChange(false);
    },
    onError: () => toast.error(`Failed to ${ruleId ? 'update' : 'create'} rule`)
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    let parsedConditions = {};
    try {
      parsedConditions = JSON.parse(conditionsString);
    } catch (err) {
      toast.error('Invalid JSON in conditions');
      return;
    }

    saveRule.mutate({
      name,
      description,
      trigger_type: triggerType,
      action_type: actionType,
      conditions: parsedConditions,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{ruleId ? 'Edit Automation Rule' : 'Create Automation Rule'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Rule Name</Label>
            <Input value={name} onChange={e => setName(e.target.value)} required placeholder="e.g. Notify on new project" />
          </div>
          
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="What does this rule do?" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Trigger Event</Label>
              <Select value={triggerType} onValueChange={setTriggerType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select Trigger" />
                </SelectTrigger>
                <SelectContent>
                  {TRIGGER_OPTIONS.map(opt => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Action</Label>
              <Select value={actionType} onValueChange={setActionType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select Action" />
                </SelectTrigger>
                <SelectContent>
                  {ACTION_OPTIONS.map(opt => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Conditions & Configuration (JSON)</Label>
            <Textarea 
              className="font-mono text-sm h-32" 
              value={conditionsString} 
              onChange={e => setConditionsString(e.target.value)} 
            />
            <p className="text-xs text-muted-foreground">Specify exact constraints or action parameters in JSON format.</p>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={saveRule.isPending || !name || !triggerType || !actionType}>
              {saveRule.isPending ? 'Saving...' : 'Save Rule'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
