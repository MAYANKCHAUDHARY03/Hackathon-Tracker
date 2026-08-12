import React, { useState } from 'react';
import { AutomationRuleList } from '@/components/automation/AutomationRuleList';
import { AutomationRuleForm } from '@/components/automation/AutomationRuleForm';
import { Zap } from 'lucide-react';
import { useWorkspaceStore } from '@/store/workspaceStore';

export default function Automation() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);

  const { activeWorkspaceId } = useWorkspaceStore();

  const handleCreateNew = () => {
    setEditingRuleId(null);
    setIsFormOpen(true);
  };

  const handleEdit = (ruleId: string) => {
    setEditingRuleId(ruleId);
    setIsFormOpen(true);
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Zap className="w-8 h-8 text-primary" />
          Workflow Automation
        </h1>
        <p className="text-muted-foreground text-lg max-w-2xl">
          Automate operations across your hackathon ecosystem. Define triggers and actions to streamline project management and user engagement.
        </p>
      </div>

      {activeWorkspaceId ? (
        <>
          <AutomationRuleList 
            onCreateClick={handleCreateNew} 
            onEditClick={handleEdit} 
          />
          <AutomationRuleForm 
            open={isFormOpen} 
            onOpenChange={setIsFormOpen} 
            ruleId={editingRuleId} 
          />
        </>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          Please select a workspace to manage automation rules.
        </div>
      )}
    </div>
  );
}
