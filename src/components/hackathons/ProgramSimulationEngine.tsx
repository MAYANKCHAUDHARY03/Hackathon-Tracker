import React, { useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Activity, Users, Settings, Database, AlertTriangle, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';

interface SimulationRisk {
  risk_factor: string;
  severity: string;
  mitigation: string;
}

interface SimulationResponse {
  expected_load: {
    total_submissions: number;
    total_evaluations: number;
    peak_concurrent_users: number;
  };
  judge_requirements: {
    ideal_count: number;
    available_count: number;
    status: string;
  };
  mentor_requirements: {
    ideal_count: number;
    available_count: number;
    status: string;
  };
  infrastructure_requirements: {
    peak_rps: number;
    recommended_tier: string;
  };
  projected_risks: SimulationRisk[];
  is_viable: boolean;
}

export function ProgramSimulationEngine() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResponse | null>(null);

  const [formData, setFormData] = useState({
    participant_count: 500,
    team_count: 100,
    rounds_count: 2,
    judges_available: 20,
    mentors_available: 10,
    evaluation_criteria_count: 5,
    duration_days: 30
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: parseInt(e.target.value) || 0 }));
  };

  const handleSimulate = async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    try {
      const response = await apiClient.post<SimulationResponse>(
        `/workspaces/${activeWorkspaceId}/program-simulation`,
        formData
      );
      setResult(response);
      toast.success('Simulation complete');
    } catch (err: any) {
      toast.error('Simulation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Program Simulation Engine</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Stress-test a program's configuration before launch. Adjust parameters to see the projected impact on resources and infrastructure.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassPanel className="p-6 lg:col-span-1 space-y-6">
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">Tunable Inputs</h3>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Participant Count</Label>
              <Input type="number" name="participant_count" value={formData.participant_count} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>Team Count</Label>
              <Input type="number" name="team_count" value={formData.team_count} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>Number of Rounds</Label>
              <Input type="number" name="rounds_count" value={formData.rounds_count} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>Judges Available</Label>
              <Input type="number" name="judges_available" value={formData.judges_available} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>Mentors Available</Label>
              <Input type="number" name="mentors_available" value={formData.mentors_available} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>Duration (Days)</Label>
              <Input type="number" name="duration_days" value={formData.duration_days} onChange={handleChange} />
            </div>
          </div>
          
          <Button onClick={handleSimulate} disabled={loading} className="w-full">
            {loading ? 'Simulating...' : 'Run Simulation'}
          </Button>
        </GlassPanel>

        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <GlassPanel className={`p-6 border-l-4 ${result.is_viable ? 'border-l-green-500' : 'border-l-red-500'}`}>
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold">Simulation Results</h3>
                  <div className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2 ${result.is_viable ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                    {result.is_viable ? <ShieldCheck className="h-4 w-4"/> : <AlertTriangle className="h-4 w-4"/>}
                    {result.is_viable ? 'Viable Configuration' : 'High Risk Configuration'}
                  </div>
                </div>
              </GlassPanel>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <GlassPanel className="p-6">
                  <h4 className="font-semibold text-sm text-muted-foreground flex items-center gap-2 mb-4">
                    <Activity className="h-4 w-4 text-blue-500" /> Expected Load
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">Total Submissions</span>
                      <span className="font-bold">{result.expected_load.total_submissions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Total Evaluations</span>
                      <span className="font-bold">{result.expected_load.total_evaluations}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Peak Concurrent Users</span>
                      <span className="font-bold">{result.expected_load.peak_concurrent_users}</span>
                    </div>
                  </div>
                </GlassPanel>

                <GlassPanel className="p-6">
                  <h4 className="font-semibold text-sm text-muted-foreground flex items-center gap-2 mb-4">
                    <Database className="h-4 w-4 text-purple-500" /> Infrastructure Requirements
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">Peak API Requests/sec</span>
                      <span className="font-bold">{result.infrastructure_requirements.peak_rps}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Recommended Tier</span>
                      <span className="font-bold">{result.infrastructure_requirements.recommended_tier}</span>
                    </div>
                  </div>
                </GlassPanel>

                <GlassPanel className="p-6 md:col-span-2">
                  <h4 className="font-semibold text-sm text-muted-foreground flex items-center gap-2 mb-4">
                    <Users className="h-4 w-4 text-amber-500" /> Staffing Requirements
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-secondary/20 rounded-lg">
                      <h5 className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">Judges</h5>
                      <div className="flex justify-between items-center">
                        <span className="text-2xl font-bold">{result.judge_requirements.available_count} <span className="text-sm font-normal text-muted-foreground">/ {result.judge_requirements.ideal_count} needed</span></span>
                        <span className={`text-xs px-2 py-1 rounded ${result.judge_requirements.status === 'SUFFICIENT' ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                          {result.judge_requirements.status}
                        </span>
                      </div>
                    </div>
                    <div className="p-4 bg-secondary/20 rounded-lg">
                      <h5 className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">Mentors</h5>
                      <div className="flex justify-between items-center">
                        <span className="text-2xl font-bold">{result.mentor_requirements.available_count} <span className="text-sm font-normal text-muted-foreground">/ {result.mentor_requirements.ideal_count} needed</span></span>
                        <span className={`text-xs px-2 py-1 rounded ${result.mentor_requirements.status === 'SUFFICIENT' ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                          {result.mentor_requirements.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </GlassPanel>
                
                <GlassPanel className="p-6 md:col-span-2">
                  <h4 className="font-semibold text-sm text-muted-foreground flex items-center gap-2 mb-4">
                    <AlertTriangle className="h-4 w-4 text-red-500" /> Projected Risks
                  </h4>
                  <div className="space-y-3">
                    {result.projected_risks.map((risk, idx) => (
                      <div key={idx} className="p-3 border border-border/50 rounded-lg bg-secondary/10 flex flex-col gap-1">
                        <div className="flex justify-between">
                          <span className="font-semibold text-sm">{risk.risk_factor}</span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${risk.severity === 'HIGH' ? 'bg-red-500/20 text-red-500' : risk.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-500' : 'bg-green-500/20 text-green-500'}`}>
                            {risk.severity}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">{risk.mitigation}</p>
                      </div>
                    ))}
                  </div>
                </GlassPanel>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center border-2 border-dashed border-border/50 rounded-xl bg-secondary/5 text-muted-foreground">
              Configure parameters and run the simulation to see projections.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
