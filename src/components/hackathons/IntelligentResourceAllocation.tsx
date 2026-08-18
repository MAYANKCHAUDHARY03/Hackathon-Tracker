import React, { useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Users, Bot, CheckCircle2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

// Mock data to simulate the inputs since we don't have real judges and projects loaded here yet
const MOCK_JUDGES = [
  { id: '11111111-1111-1111-1111-111111111111', name: 'Dr. Sarah Chen', expertise: ['AI', 'Healthcare'], conflicts: [], max_workload: 5 },
  { id: '22222222-2222-2222-2222-222222222222', name: 'James Wilson', expertise: ['Fintech', 'Blockchain'], conflicts: [], max_workload: 3 },
  { id: '33333333-3333-3333-3333-333333333333', name: 'Elena Rodriguez', expertise: ['AI', 'Sustainability'], conflicts: ['55555555-5555-5555-5555-555555555555'], max_workload: 4 },
  { id: '44444444-4444-4444-4444-444444444444', name: 'Michael Chang', expertise: ['EdTech', 'Mobile'], conflicts: [], max_workload: 5 }
];

const MOCK_PROJECTS = [
  { id: '55555555-5555-5555-5555-555555555555', name: 'MediPredict AI', domains: ['AI', 'Healthcare'] },
  { id: '66666666-6666-6666-6666-666666666666', name: 'GreenChain', domains: ['Blockchain', 'Sustainability'] },
  { id: '77777777-7777-7777-7777-777777777777', name: 'LearnFlow', domains: ['EdTech', 'AI'] }
];

interface AllocationResult {
  project_id: string;
  judge_ids: string[];
  explanation: string;
}

interface AllocationResponse {
  allocations: AllocationResult[];
  unallocated_projects: string[];
}

export function IntelligentResourceAllocation({ hackathonId }: { hackathonId: string }) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AllocationResponse | null>(null);

  const handleAllocate = async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    try {
      const response = await apiClient.post<AllocationResponse>(
        `/workspaces/${activeWorkspaceId}/hackathons/${hackathonId}/allocate-judges`,
        {
          judges: MOCK_JUDGES,
          projects: MOCK_PROJECTS,
          judges_per_project: 2
        }
      );
      setResult(response);
      toast.success('Allocation complete');
    } catch (err: any) {
      toast.error('Allocation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getJudgeName = (id: string) => MOCK_JUDGES.find(j => j.id === id)?.name || id;
  const getProjectName = (id: string) => MOCK_PROJECTS.find(p => p.id === id)?.name || id;

  return (
    <GlassPanel className="p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" /> Intelligent Resource Allocation
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Deterministically assign judges based on expertise, workload, and conflicts, with AI explanations.
          </p>
        </div>
        <Button onClick={handleAllocate} disabled={loading} className="gap-2">
          <Users className="h-4 w-4" />
          {loading ? 'Running...' : 'Run Allocation'}
        </Button>
      </div>

      {result ? (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="grid grid-cols-1 gap-4">
            {result.allocations.map((alloc, idx) => (
              <div key={idx} className="p-4 border border-border/50 rounded-lg bg-secondary/10">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <h4 className="font-semibold">{getProjectName(alloc.project_id)}</h4>
                </div>
                <div className="space-y-2 mt-3">
                  <p className="text-sm font-medium">Assigned Judges:</p>
                  <div className="flex flex-wrap gap-2">
                    {alloc.judge_ids.map(id => (
                      <span key={id} className="px-2 py-1 text-xs rounded-full bg-primary/10 text-primary font-medium">
                        {getJudgeName(id)}
                      </span>
                    ))}
                  </div>
                  <div className="mt-4 p-3 bg-card/50 rounded text-xs text-muted-foreground border-l-2 border-primary italic">
                    <span className="font-semibold block mb-1 text-foreground">Constraint Engine Explanation:</span>
                    {alloc.explanation}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {result.unallocated_projects.length > 0 && (
            <div className="p-4 border border-red-500/20 rounded-lg bg-red-500/5">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <h4 className="font-semibold text-red-500">Unallocated Projects</h4>
              </div>
              <ul className="list-disc pl-5 text-sm text-red-500/80">
                {result.unallocated_projects.map(id => (
                  <li key={id}>{getProjectName(id)}</li>
                ))}
              </ul>
              <p className="text-xs text-red-500/60 mt-2">Could not assign sufficient judges due to strict constraints.</p>
            </div>
          )}
        </div>
      ) : (
        <div className="h-32 flex items-center justify-center border-2 border-dashed border-border/50 rounded-xl bg-secondary/5 text-muted-foreground text-sm">
          Click "Run Allocation" to see the engine in action.
        </div>
      )}
    </GlassPanel>
  );
}
