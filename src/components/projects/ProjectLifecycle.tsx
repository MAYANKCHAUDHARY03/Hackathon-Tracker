import { useEffect, useState } from "react";
import { projectsApi, type ProjectTransition } from "@/api/projectsApi";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { format } from "date-fns";
import { CheckCircle2, Circle, GitCommit, Loader2 } from "lucide-react";

const LIFECYCLE_STATES = [
  "IDEA", "PROTOTYPE", "VALIDATION", "MVP", "INCUBATION", "PILOT", "PRODUCTION", "ARCHIVED"
];

interface ProjectLifecycleProps {
  workspaceId: string;
  projectId: string;
  currentStatus: string;
  onStatusChange?: (newStatus: string) => void;
}

export function ProjectLifecycle({ workspaceId, projectId, currentStatus, onStatusChange }: ProjectLifecycleProps) {
  const [transitions, setTransitions] = useState<ProjectTransition[]>([]);
  const [loading, setLoading] = useState(true);
  const [newState, setNewState] = useState("");
  const [notes, setNotes] = useState("");
  const [transitioning, setTransitioning] = useState(false);

  const loadTransitions = async () => {
    try {
      const res = await projectsApi.getTransitions(workspaceId, projectId);
      setTransitions(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransitions();
  }, [workspaceId, projectId]);

  const handleTransition = async () => {
    if (!newState) return;
    setTransitioning(true);
    try {
      await projectsApi.transitionState(workspaceId, projectId, { state: newState, notes });
      setNewState("");
      setNotes("");
      await loadTransitions();
      onStatusChange?.(newState);
    } catch (err) {
      console.error("Transition failed", err);
    } finally {
      setTransitioning(false);
    }
  };

  if (loading) {
    return <div className="py-8 flex justify-center"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="font-semibold text-lg mb-4">Advance Project State</h3>
        <div className="flex gap-4 items-end">
          <div className="space-y-1 flex-1">
            <label className="text-sm font-medium">Next State</label>
            <Select value={newState} onValueChange={setNewState}>
              <SelectTrigger>
                <SelectValue placeholder="Select new state..." />
              </SelectTrigger>
              <SelectContent>
                {LIFECYCLE_STATES.map(s => (
                  <SelectItem key={s} value={s} disabled={s.toLowerCase() === currentStatus?.toLowerCase()}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1 flex-[2]">
            <label className="text-sm font-medium">Transition Notes</label>
            <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="e.g. Completed initial user testing..." />
          </div>
          <Button onClick={handleTransition} disabled={!newState || transitioning}>
            {transitioning ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <GitCommit className="h-4 w-4 mr-2" />}
            Transition
          </Button>
        </div>
      </div>

      <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
        {transitions.map((t, i) => (
          <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className="flex items-center justify-center w-10 h-10 rounded-full border border-background bg-secondary text-primary shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              <CheckCircle2 className="h-5 w-5" />
            </div>
            <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-border bg-card shadow">
              <div className="flex items-center justify-between mb-1">
                <div className="font-bold text-primary">{t.state}</div>
                <time className="text-xs font-medium text-muted-foreground">{format(new Date(t.transitioned_at), "PPp")}</time>
              </div>
              {t.notes && <div className="text-sm text-muted-foreground mb-2">{t.notes}</div>}
              <div className="text-xs text-muted-foreground font-medium flex items-center gap-1">
                <Circle className="h-3 w-3 fill-primary text-primary" />
                By {t.actor_name}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
