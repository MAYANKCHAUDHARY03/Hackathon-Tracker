import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bot, AlertTriangle, Activity, CheckCircle, Play } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/config';

interface OrganizerCopilotRecommendedAction {
  action_type: string;
  description: string;
  reason: string;
  expected_impact: string;
  target_entity_id?: string;
  target_entity_type?: string;
  payload?: any;
}

interface OrganizerCopilotStatus {
  hackathon_id: string;
  overall_health: string;
  incomplete_submissions: number;
  missing_demos: number;
  incomplete_evaluations: number;
  risk_flags: string[];
  recommended_actions: OrganizerCopilotRecommendedAction[];
}

interface OrganizerCopilotProps {
  hackathonId: string;
  workspaceId: string;
}

export function OrganizerCopilot({ hackathonId, workspaceId }: OrganizerCopilotProps) {
  const [status, setStatus] = useState<OrganizerCopilotStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();
  const { toast } = useToast();

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/hackathons/${hackathonId}/copilot`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch organizer copilot status', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [hackathonId, workspaceId]);

  const executeAction = async (action: OrganizerCopilotRecommendedAction) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/hackathons/${hackathonId}/copilot/action`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });
      const data = await response.json();
      if (response.ok) {
        if (data.status === "pending_approval") {
          toast({
            title: 'Approval Requested',
            description: 'Action sent to Agent Approvals queue.',
          });
        } else {
          toast({
            title: 'Action Executed',
            description: 'Copilot action executed successfully.',
          });
        }
        fetchStatus();
      } else {
        toast({
          title: 'Execution Failed',
          description: data.detail || 'Failed to execute action',
          variant: 'destructive'
        });
      }
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) return <div>Loading Organizer Copilot...</div>;
  if (!status) return null;

  return (
    <Card className="border-teal-500/20 bg-slate-900/50 backdrop-blur-sm shadow-xl">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-teal-400" />
          <CardTitle>Organizer Copilot</CardTitle>
        </div>
        <Badge variant={status.overall_health === 'Healthy' ? 'default' : 'destructive'} className={status.overall_health === 'Healthy' ? 'bg-teal-500/20 text-teal-300' : ''}>
          {status.overall_health}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        
        <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-800">
          <div className="text-center p-2 rounded bg-slate-800/50">
            <div className="text-2xl font-bold text-slate-200">{status.incomplete_submissions}</div>
            <div className="text-xs text-slate-400">Incomplete Subs</div>
          </div>
          <div className="text-center p-2 rounded bg-slate-800/50">
            <div className="text-2xl font-bold text-slate-200">{status.missing_demos}</div>
            <div className="text-xs text-slate-400">Missing Demos</div>
          </div>
          <div className="text-center p-2 rounded bg-slate-800/50">
            <div className="text-2xl font-bold text-slate-200">{status.incomplete_evaluations}</div>
            <div className="text-xs text-slate-400">Pending Evals</div>
          </div>
        </div>

        {status.risk_flags.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center text-amber-400">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Program Risks
            </h4>
            <ul className="text-sm space-y-1 text-slate-300">
              {status.risk_flags.map((risk, i) => (
                <li key={i} className="flex items-start">
                  <span className="mr-2">•</span> {risk}
                </li>
              ))}
            </ul>
          </div>
        )}

        {status.recommended_actions.length > 0 && (
          <div className="space-y-3 pt-2">
            <h4 className="text-sm font-medium flex items-center text-teal-400">
              <CheckCircle className="h-4 w-4 mr-2" />
              Recommended Actions
            </h4>
            <div className="space-y-3">
              {status.recommended_actions.map((action, i) => (
                <div key={i} className="flex flex-col p-3 rounded-md bg-slate-800/50 border border-slate-700/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-slate-200">{action.description}</span>
                    <Button size="sm" variant="outline" className="h-7 border-teal-500/30 text-teal-400 hover:bg-teal-500/10 hover:text-teal-300" onClick={() => executeAction(action)}>
                      <Play className="h-3 w-3 mr-1" /> Execute
                    </Button>
                  </div>
                  <p className="text-xs text-slate-400"><strong className="text-slate-300">Reason:</strong> {action.reason}</p>
                  <p className="text-xs text-slate-400"><strong className="text-slate-300">Impact:</strong> {action.expected_impact}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
