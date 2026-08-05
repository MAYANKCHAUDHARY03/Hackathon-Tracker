import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { roundApi, HackathonRound, Deadline } from '@/api/roundApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { useHackathonStore } from '@/store/hackathonStore';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';

export default function HackathonDetails() {
  const { id } = useParams<{ id: string }>();
  const activeWorkspace = useWorkspaceStore((s) => s.activeWorkspace);
  const hackathons = useHackathonStore((s) => s.hackathons);
  
  const [rounds, setRounds] = useState<HackathonRound[]>([]);
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  
  const hackathon = hackathons.byId[id || ''];

  useEffect(() => {
    if (activeWorkspace && id) {
      roundApi.getRounds(id).then(setRounds).catch(console.error);
      roundApi.getDeadlines(id).then(setDeadlines).catch(console.error);
    }
  }, [activeWorkspace, id]);

  if (!hackathon) {
    return <div className="p-8">Hackathon not found or loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{hackathon.name}</h1>
        <p className="text-muted-foreground">{hackathon.description}</p>
      </div>

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
    </div>
  );
}
