import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, Lightbulb, AlertTriangle, List, BookOpen } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/config';

interface MentorRecommendedResource {
  title: string;
  url: string;
  reason: string;
}

interface MentorCopilotBrief {
  project_id: string;
  team_name: string;
  project_title: string;
  progress_summary: string;
  recent_activity: string[];
  flagged_blockers: string[];
  suggested_agenda: string[];
  recommended_resources: MentorRecommendedResource[];
}

interface MentorCopilotProps {
  projectId: string;
  workspaceId: string;
}

export function MentorCopilot({ projectId, workspaceId }: MentorCopilotProps) {
  const [brief, setBrief] = useState<MentorCopilotBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuthStore();
  const { toast } = useToast();

  const fetchBrief = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/${workspaceId}/projects/${projectId}/mentor-copilot`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setBrief(data);
      } else {
        toast({ title: 'Failed to load brief', variant: 'destructive' });
      }
    } catch (error) {
      console.error('Failed to fetch mentor copilot brief', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrief();
  }, [projectId, workspaceId]);

  if (loading) return <div>Generating Mentor Brief...</div>;
  if (!brief) return null;

  return (
    <Card className="border-indigo-500/20 bg-slate-900/50 backdrop-blur-sm shadow-xl">
      <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-indigo-400" />
          <CardTitle>Mentor Meeting Brief</CardTitle>
        </div>
        <Badge variant="outline" className="border-indigo-500/30 text-indigo-300 bg-indigo-500/10">
          AI Generated
        </Badge>
      </CardHeader>
      <CardContent className="space-y-6 pt-6">
        
        <div className="space-y-2">
          <h4 className="text-sm font-medium flex items-center text-slate-200">
            <Lightbulb className="h-4 w-4 mr-2 text-indigo-400" />
            Executive Summary
          </h4>
          <p className="text-sm text-slate-400 bg-slate-800/30 p-3 rounded-md border border-slate-800">
            {brief.progress_summary}
          </p>
        </div>

        {brief.flagged_blockers.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center text-amber-400">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Flagged Blockers
            </h4>
            <ul className="text-sm space-y-2 text-slate-300">
              {brief.flagged_blockers.map((blocker, i) => (
                <li key={i} className="flex items-start bg-amber-500/10 border border-amber-500/20 p-2 rounded">
                  <span className="mr-2 text-amber-500">•</span> {blocker}
                </li>
              ))}
            </ul>
          </div>
        )}

        {brief.suggested_agenda.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center text-emerald-400">
              <List className="h-4 w-4 mr-2" />
              Suggested Agenda
            </h4>
            <ol className="text-sm space-y-1 text-slate-300 list-decimal list-inside pl-1 bg-slate-800/30 p-3 rounded-md border border-slate-800">
              {brief.suggested_agenda.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ol>
          </div>
        )}

        {brief.recommended_resources.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <h4 className="text-sm font-medium flex items-center text-sky-400 mb-3">
              <BookOpen className="h-4 w-4 mr-2" />
              Recommended Resources to Share
            </h4>
            <div className="space-y-3">
              {brief.recommended_resources.map((res, i) => (
                <div key={i} className="flex flex-col p-3 rounded-md bg-slate-800/50 border border-slate-700/50">
                  <a href={res.url} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-sky-400 hover:underline mb-1">
                    {res.title}
                  </a>
                  <p className="text-xs text-slate-400">{res.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}

      </CardContent>
    </Card>
  );
}
