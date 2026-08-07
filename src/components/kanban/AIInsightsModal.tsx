import { useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Brain, X, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface AIInsightsModalProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
}

interface AIHealthData {
  health_status: string;
  risk_score: number;
  recommendations: string[];
}

export function AIInsightsModal({ projectId, isOpen, onClose }: AIInsightsModalProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [healthData, setHealthData] = useState<AIHealthData | null>(null);

  if (!isOpen) return null;

  async function fetchInsights() {
    setLoading(true);
    try {
      const summaryRes = await apiClient.get<{ summary: string }>(`/workspaces/${activeWorkspaceId}/projects/${projectId}/ai/summary`);
      const healthRes = await apiClient.get<AIHealthData>(`/workspaces/${activeWorkspaceId}/projects/${projectId}/ai/health`);
      
      setSummary(summaryRes.summary);
      setHealthData(healthRes);
    } catch (err) {
      console.error(err);
      alert('Failed to fetch AI insights');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
      <GlassPanel className="w-full max-w-2xl overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-4 border-b border-border/50">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-primary/20 rounded-md">
              <Brain className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-lg font-semibold tracking-tight">AI Project Insights</h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {!summary && !loading && (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">Generate AI-powered insights about your project's health and progress.</p>
              <Button onClick={fetchInsights} className="gap-2">
                <Brain className="h-4 w-4" />
                Generate Insights
              </Button>
            </div>
          )}

          {loading && (
            <div className="text-center py-8 space-y-4">
              <Brain className="h-8 w-8 text-primary animate-pulse mx-auto" />
              <p className="text-muted-foreground">Analyzing project data...</p>
            </div>
          )}

          {summary && healthData && !loading && (
            <div className="space-y-6">
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-muted-foreground">Project Summary</h3>
                <p className="text-sm bg-secondary/30 p-4 rounded-lg border border-border/50">
                  {summary}
                </p>
              </div>

              <div className="space-y-2">
                <h3 className="text-sm font-medium text-muted-foreground">Health Analysis</h3>
                <div className={`p-4 rounded-lg border flex items-start gap-4 ${
                  healthData.health_status === 'healthy' 
                    ? 'bg-green-500/10 border-green-500/20' 
                    : 'bg-yellow-500/10 border-yellow-500/20'
                }`}>
                  {healthData.health_status === 'healthy' ? (
                    <CheckCircle2 className="h-6 w-6 text-green-500 mt-1" />
                  ) : (
                    <AlertTriangle className="h-6 w-6 text-yellow-500 mt-1" />
                  )}
                  
                  <div>
                    <p className="font-semibold capitalize flex items-center gap-2">
                      {healthData.health_status.replace('_', ' ')}
                      <span className="text-xs font-normal opacity-70">Risk Score: {healthData.risk_score}/100</span>
                    </p>
                    <div className="mt-2 space-y-1">
                      {healthData.recommendations.map((rec, i) => (
                        <p key={i} className="text-sm flex items-center gap-2">
                          <span className="w-1 h-1 rounded-full bg-current opacity-50" />
                          {rec}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </GlassPanel>
    </div>
  );
}
