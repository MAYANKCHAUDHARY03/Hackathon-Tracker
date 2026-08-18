import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bot, Play, CheckCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/config';

interface ProjectAgentEvaluationProps {
  projectId: string;
  workspaceId: string;
}

export function ProjectAgentEvaluation({ projectId, workspaceId }: ProjectAgentEvaluationProps) {
  const [loading, setLoading] = useState(false);
  const [evaluations, setEvaluations] = useState<any[]>([]);
  const { token } = useAuth();
  const { toast } = useToast();
  
  // Need hackathon_id to fetch templates. We can fetch project details first.
  const [hackathonId, setHackathonId] = useState<string | null>(null);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  useEffect(() => {
    const fetchProjectAndEvaluations = async () => {
      try {
        // Fetch project to get hackathon_id
        const projRes = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/projects`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (projRes.ok) {
          const projs = await projRes.json();
          const p = projs.find((x: any) => x.id === projectId);
          if (p && p.hackathon_id) {
            setHackathonId(p.hackathon_id);
            
            // Fetch templates
            const tplRes = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/hackathons/${p.hackathon_id}/evaluation-templates`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            if (tplRes.ok) {
              const tpls = await tplRes.json();
              setTemplates(tpls);
              if (tpls.length > 0) setSelectedTemplate(tpls[0].id);
            }
          }
        }
      } catch (err) {
        console.error("Failed to load project details", err);
      }
    };
    fetchProjectAndEvaluations();
  }, [projectId, workspaceId]);

  const runAgentEvaluation = async () => {
    if (!hackathonId || !selectedTemplate) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/hackathons/${hackathonId}/agent-evaluation`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: projectId,
          template_id: selectedTemplate
        })
      });
      if (response.ok) {
        const data = await response.json();
        setEvaluations(prev => [...prev, data]);
        toast({ title: 'AI Evaluation Complete', description: 'Preliminary evaluation generated.' });
      } else {
        toast({ title: 'Evaluation Failed', variant: 'destructive' });
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (!hackathonId) return <div className="text-sm text-slate-400">Loading evaluation context...</div>;

  return (
    <Card className="border-indigo-500/20 bg-slate-900/50 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-indigo-400" />
          <CardTitle>Agent Evaluation (Phase 54)</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {templates.length === 0 ? (
          <p className="text-sm text-slate-400">No evaluation templates available in this hackathon.</p>
        ) : (
          <div className="flex items-center space-x-2">
            <select 
              className="bg-slate-800 border border-slate-700 text-sm rounded-md p-2 flex-1"
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
            >
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
            <Button onClick={runAgentEvaluation} disabled={loading} className="bg-indigo-600 hover:bg-indigo-700">
              {loading ? "Evaluating..." : <><Play className="h-4 w-4 mr-2" /> Run AI Evaluation</>}
            </Button>
          </div>
        )}

        {evaluations.length > 0 && (
          <div className="space-y-3 mt-4">
            <h4 className="text-sm font-medium text-slate-200">Recent AI Evaluations</h4>
            {evaluations.map((ev, i) => (
              <div key={i} className="p-3 bg-slate-800/50 rounded-md border border-indigo-500/30">
                <div className="flex justify-between items-center mb-2">
                  <Badge variant="outline" className="text-amber-400 border-amber-400/50 bg-amber-400/10">
                    {ev.status}
                  </Badge>
                  <span className="text-xs text-slate-400">Source: {ev.source}</span>
                </div>
                <p className="text-sm text-slate-300 italic mb-2">"{ev.overall_feedback}"</p>
                <div className="space-y-1">
                  {ev.scores?.map((score: any, j: number) => (
                    <div key={j} className="flex justify-between text-xs p-1 bg-slate-900/50 rounded">
                      <span className="text-slate-300 truncate w-3/4" title={score.feedback}>{score.feedback}</span>
                      <span className="text-indigo-300 font-mono">{score.numeric_score} pts</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
