import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useHackathonStore } from '@/store/hackathonStore';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { MentorsJudgesTab } from '@/components/evaluations/MentorsJudgesTab';
import { EvaluationsTab } from '@/components/evaluations/EvaluationsTab';
import { OutcomesTab } from '@/components/evaluations/OutcomesTab';
import { FormsTab } from '@/components/forms/FormsTab';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';
import { Users, ClipboardList, Trophy, Calendar, BarChart } from 'lucide-react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { roundApi } from '@/api/roundApi';
import type { HackathonRound, Deadline } from '@/api/roundApi';

export default function HackathonDetails() {
  const { id } = useParams<{ id: string }>();
  const hackathons = useHackathonStore(s => s.hackathons);
  const currentWorkspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  
  const [rounds, setRounds] = useState<HackathonRound[]>([]);
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'personnel' | 'evaluations' | 'outcomes' | 'forms' | 'analytics'>('overview');
  
  const hackathon = hackathons.byId[id || ''];

  useEffect(() => {
    if (id && currentWorkspaceId) {
      roundApi.getRounds(id).then(setRounds).catch(console.error);
      roundApi.getDeadlines(id).then(setDeadlines).catch(console.error);
    }
  }, [id, currentWorkspaceId]);

  if (!hackathon) {
    return <div className="p-8">Hackathon not found or loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold">{hackathon.name}</h1>
          {hackathon.program_type && (
            <span className="text-xs font-semibold px-2 py-1 rounded bg-secondary text-secondary-foreground uppercase tracking-wider">
              {hackathon.program_type}
            </span>
          )}
          {hackathon.is_template && (
            <span className="text-xs font-semibold px-2 py-1 rounded bg-primary/20 text-primary uppercase tracking-wider">
              Template
            </span>
          )}
        </div>
        <p className="text-muted-foreground mt-2">{hackathon.description}</p>
      </div>

      <div className="flex border-b border-border/50 gap-6">
        <button 
          onClick={() => setActiveTab('overview')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${activeTab === 'overview' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          <Calendar className="h-4 w-4" />
          Overview
        </button>
        <button 
          onClick={() => setActiveTab('personnel')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${activeTab === 'personnel' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          <Users className="h-4 w-4" />
          Mentors & Judges
        </button>
        <button 
          onClick={() => setActiveTab('evaluations')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${activeTab === 'evaluations' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          <ClipboardList className="h-4 w-4" />
          Evaluations
        </button>
        <button 
          onClick={() => setActiveTab('outcomes')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${activeTab === 'outcomes' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          <Trophy className="h-4 w-4" />
          Results & Rewards
        </button>
        <button 
          onClick={() => setActiveTab('forms')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${activeTab === 'forms' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          <ClipboardList className="h-4 w-4" />
          Application Forms
        </button>
        <button 
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${activeTab === 'analytics' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          <BarChart className="h-4 w-4" />
          Analytics
        </button>
      </div>

      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="grid gap-6 md:grid-cols-2">
            <GlassPanel className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Rounds</h2>
                <Button size="sm">Add Round</Button>
              </div>
              {rounds.length === 0 ? (
                <p className="text-sm text-muted-foreground">No rounds defined.</p>
              ) : (
                <div className="space-y-2">
                  {rounds.map(r => (
                    <div key={r.id} className="p-3 bg-card rounded-md border">
                      <div className="font-medium">{r.name}</div>
                      <div className="text-sm text-muted-foreground">Type: {r.round_type}</div>
                    </div>
                  ))}
                </div>
              )}
            </GlassPanel>

            <GlassPanel className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Deadlines</h2>
                <Button size="sm">Add Deadline</Button>
              </div>
              {deadlines.length === 0 ? (
                <p className="text-sm text-muted-foreground">No deadlines defined.</p>
              ) : (
                <div className="space-y-2">
                  {deadlines.map(d => (
                    <div key={d.id} className="p-3 bg-card rounded-md border">
                      <div className="font-medium">{d.name}</div>
                      <div className="text-sm text-muted-foreground">Due: {new Date(d.due_at).toLocaleString()}</div>
                    </div>
                  ))}
                </div>
              )}
            </GlassPanel>
          </div>
        )}

        {activeTab === 'personnel' && id && <MentorsJudgesTab hackathonId={id} />}
        {activeTab === 'evaluations' && id && <EvaluationsTab hackathonId={id} />}
        {activeTab === 'outcomes' && id && <OutcomesTab hackathonId={id} />}
        {activeTab === 'forms' && id && <FormsTab hackathonId={id} />}
        {activeTab === 'analytics' && <AnalyticsDashboard />}
      </div>
    </div>
  );
}
