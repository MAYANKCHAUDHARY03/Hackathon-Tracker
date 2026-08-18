import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Bot, AlertTriangle, CheckCircle, Activity, Play } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/config';

interface CopilotRecommendedAction {
  action_type: string;
  description: string;
  target_entity_id?: string;
  target_entity_type?: string;
  payload?: any;
}

interface ProjectCopilotStatus {
  project_id: string;
  status: string;
  progress_percent: number;
  risk_flags: string[];
  detected_issues: string[];
  recommended_actions: CopilotRecommendedAction[];
}

interface ProjectCopilotProps {
  projectId: string;
  workspaceId: string;
}

export function ProjectCopilot({ projectId, workspaceId }: ProjectCopilotProps) {
  const [status, setStatus] = useState<ProjectCopilotStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuthStore();
  const { toast } = useToast();

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/projects/${projectId}/copilot`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch copilot status', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [projectId, workspaceId]);

  const executeAction = async (action: CopilotRecommendedAction) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/projects/${projectId}/copilot/action`, {
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
        // Refresh status
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

  if (loading) return <div>Loading Project Copilot...</div>;
  if (!status) return null;

  return (
    <Card className="border-teal-500/20 bg-slate-900/50 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-teal-400" />
          <CardTitle>Project Copilot</CardTitle>
        </div>
        <Badge variant={status.status === 'On Track' ? 'default' : 'destructive'} className={status.status === 'On Track' ? 'bg-teal-500/20 text-teal-300' : ''}>
          {status.status}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-slate-400">
            <span>Project Progress</span>
            <span>{status.progress_percent}%</span>
          </div>
          <Progress value={status.progress_percent} className="h-2 bg-slate-800" />
        </div>

        {status.risk_flags.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center text-amber-400">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Risk Flags
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

        {status.detected_issues.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center text-rose-400">
              <Activity className="h-4 w-4 mr-2" />
              Detected Issues
            </h4>
            <ul className="text-sm space-y-1 text-slate-300">
              {status.detected_issues.map((issue, i) => (
                <li key={i} className="flex items-start">
                  <span className="mr-2">•</span> {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {status.recommended_actions.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <h4 className="text-sm font-medium flex items-center text-teal-400 mb-3">
              <CheckCircle className="h-4 w-4 mr-2" />
              Recommended Actions
            </h4>
            <div className="space-y-2">
              {status.recommended_actions.map((action, i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded-md bg-slate-800/50 border border-slate-700/50">
                  <span className="text-sm text-slate-300">{action.description}</span>
                  <Button size="sm" variant="outline" className="h-7 border-teal-500/30 text-teal-400 hover:bg-teal-500/10 hover:text-teal-300" onClick={() => executeAction(action)}>
                    <Play className="h-3 w-3 mr-1" /> Execute
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
