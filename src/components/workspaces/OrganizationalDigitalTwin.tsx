import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Activity, Play, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/config';

interface OrganizationalDigitalTwinProps {
  workspaceId: string;
}

export function OrganizationalDigitalTwin({ workspaceId }: OrganizationalDigitalTwinProps) {
  const [loading, setLoading] = useState(false);
  const [targetTeams, setTargetTeams] = useState<number | ''>('');
  const [complexity, setComplexity] = useState<number>(1.0);
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const { token } = useAuthStore();
  const { toast } = useToast();

  const runSimulation = async () => {
    setLoading(true);
    setSimulationResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/digital-twin/simulate`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          target_teams_count: targetTeams === '' ? null : targetTeams,
          complexity_multiplier: complexity
        })
      });
      if (response.ok) {
        const data = await response.json();
        setSimulationResult(data);
        toast({ title: 'Simulation Complete', description: 'Digital twin projections generated.' });
      } else {
        toast({ title: 'Simulation Failed', variant: 'destructive' });
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-indigo-500/20 bg-slate-900/50 backdrop-blur-sm">
      <CardHeader className="pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-indigo-400" />
          <CardTitle>Organizational Digital Twin</CardTitle>
        </div>
        <CardDescription className="text-slate-400 mt-2">
          Run "what-if" simulations on your innovation ecosystem to project resource needs and identify risks before committing to program changes.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 pt-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Target Teams Count (Optional)</label>
            <Input 
              type="number" 
              placeholder="e.g. 100" 
              value={targetTeams} 
              onChange={(e) => setTargetTeams(e.target.value ? parseInt(e.target.value) : '')}
              className="bg-slate-800 border-slate-700"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Complexity Multiplier (1.0 = standard)</label>
            <Input 
              type="number" 
              step="0.1"
              min="0.5"
              max="3.0"
              value={complexity} 
              onChange={(e) => setComplexity(parseFloat(e.target.value) || 1.0)}
              className="bg-slate-800 border-slate-700"
            />
          </div>
        </div>

        <Button onClick={runSimulation} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
          {loading ? "Simulating Ecosystem..." : <><Play className="h-4 w-4 mr-2" /> Run Simulation</>}
        </Button>

        {simulationResult && (
          <div className="mt-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-800/80 rounded-lg border border-slate-700 text-center">
                <div className="text-sm text-slate-400 mb-1">Judges Needed</div>
                <div className="text-2xl font-semibold text-indigo-300">{simulationResult.projected_judges_needed}</div>
              </div>
              <div className="p-4 bg-slate-800/80 rounded-lg border border-slate-700 text-center">
                <div className="text-sm text-slate-400 mb-1">Mentors Needed</div>
                <div className="text-2xl font-semibold text-indigo-300">{simulationResult.projected_mentors_needed}</div>
              </div>
              <div className="p-4 bg-slate-800/80 rounded-lg border border-slate-700 text-center">
                <div className="text-sm text-slate-400 mb-1">Est. Infra Cost</div>
                <div className="text-2xl font-semibold text-emerald-400">${simulationResult.projected_infrastructure_cost.toLocaleString()}</div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-200 mb-3 flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2 text-amber-500" />
                Resource Projections & Risks
              </h4>
              <div className="space-y-3">
                {simulationResult.resource_projections.map((rp: any, i: number) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-slate-800/40 rounded-md border border-slate-700/50">
                    <div>
                      <div className="font-medium text-slate-300">{rp.category}</div>
                      <div className="text-xs text-slate-500">Current: {rp.current_capacity} | Required: {rp.projected_requirement}</div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="text-sm text-slate-400">Gap: <span className={rp.gap > 0 ? "text-red-400 font-medium" : "text-emerald-400"}>{rp.gap > 0 ? `-${rp.gap}` : 'OK'}</span></div>
                      <Badge variant="outline" className={
                        rp.risk_level === 'HIGH' ? 'border-red-500 text-red-400' :
                        rp.risk_level === 'MEDIUM' ? 'border-amber-500 text-amber-400' :
                        'border-emerald-500 text-emerald-400'
                      }>
                        {rp.risk_level} RISK
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-200 mb-2">Simulation Insights</h4>
              <ul className="list-disc pl-5 space-y-1">
                {simulationResult.insights.map((insight: string, i: number) => (
                  <li key={i} className="text-sm text-slate-300">{insight}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
