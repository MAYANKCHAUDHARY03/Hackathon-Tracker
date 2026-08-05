import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import type { SubmissionRequirement, RoundSubmission } from '@/api/submissionApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { submissionApi } from '@/api/submissionApi';

export default function SubmissionWorkspace() {
  const { id, roundId, teamId } = useParams<{ id: string; roundId: string; teamId: string }>();
  const currentWorkspaceId = useWorkspaceStore((s) => s.activeWorkspaceId);

  const [requirements, setRequirements] = useState<SubmissionRequirement[]>([]);
  const [submission, setSubmission] = useState<RoundSubmission | null>(null);

  useEffect(() => {
    if (currentWorkspaceId && id && roundId && teamId) {
      submissionApi.getRequirements(id, roundId).then(setRequirements).catch(console.error);
      submissionApi.getSubmission(id, roundId, teamId).then(setSubmission).catch(console.error);
    }
  }, [currentWorkspaceId, id, roundId, teamId]);

  const handleUpdateItem = async (reqId: string, content: string) => {
    if (!id || !roundId || !teamId) return;
    try {
      await submissionApi.updateItem(id, roundId, teamId, { requirement_id: reqId, content });
      // Refresh submission
      const updated = await submissionApi.getSubmission(id, roundId, teamId);
      setSubmission(updated);
    } catch (e) {
      console.error('Failed to update item:', e);
    }
  };

  const handleLock = async () => {
    if (!id || !roundId || !teamId) return;
    try {
      await submissionApi.lockSubmission(id, roundId, teamId);
      // Refresh submission
      const updated = await submissionApi.getSubmission(id, roundId, teamId);
      setSubmission(updated);
    } catch (e) {
      console.error('Failed to lock submission:', e);
    }
  };

  const isLocked = submission?.status === 'locked';
  
  // Readiness calculation
  const isReady = requirements.length > 0 && requirements.every(req => {
    if (!req.is_required) return true;
    const item = submission?.items?.find(i => i.requirement_id === req.id);
    return item?.is_valid === true;
  });

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Submission Workspace</h1>
          <p className="text-muted-foreground">Manage your team's submission for this round.</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${isLocked ? 'bg-destructive/10 text-destructive' : 'bg-primary/10 text-primary'}`}>
            Status: {submission?.status || 'Not Started'}
          </div>
          {!isLocked && (
            <Button 
              variant="default" 
              disabled={!isReady} 
              onClick={handleLock}
            >
              Lock Submission
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-6">
        <GlassPanel className="p-6 space-y-6">
          <h2 className="text-xl font-semibold">Requirements</h2>
          
          <div className="space-y-4">
            {requirements.length === 0 ? (
              <p className="text-sm text-muted-foreground">No requirements configured for this round.</p>
            ) : (
              requirements.map((req) => {
                const item = submission?.items?.find(i => i.requirement_id === req.id);
                return (
                  <div key={req.id} className="p-4 border rounded-md bg-card/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {req.title} {req.is_required && <span className="text-destructive">*</span>}
                      </span>
                      <span className={`text-xs ${item?.is_valid ? 'text-green-500' : 'text-yellow-500'}`}>
                        {item?.is_valid ? 'Valid' : 'Pending'}
                      </span>
                    </div>
                    {req.description && <p className="text-sm text-muted-foreground">{req.description}</p>}
                    
                    <input 
                      className="w-full mt-2 flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                      disabled={isLocked}
                      defaultValue={item?.content || ''}
                      placeholder={`Enter ${req.requirement_type}...`}
                      onBlur={(e) => {
                        if (e.target.value !== item?.content) {
                          handleUpdateItem(req.id, e.target.value);
                        }
                      }}
                    />
                  </div>
                );
              })
            )}
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
