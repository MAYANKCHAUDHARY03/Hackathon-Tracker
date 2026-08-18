import { useState, useEffect } from "react";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { peopleApi } from "@/api/people";
import type { MentorAssignment, JudgeAssignment } from "@/api/people";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Button } from "@/components/ui/button";
import { GraduationCap, Gavel } from "lucide-react";
import { IntelligentResourceAllocation } from "@/components/hackathons/IntelligentResourceAllocation";

interface MentorsJudgesTabProps {
  hackathonId: string;
}

export function MentorsJudgesTab({ hackathonId }: MentorsJudgesTabProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [mentors, setMentors] = useState<MentorAssignment[]>([]);
  const [judges, setJudges] = useState<JudgeAssignment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (activeWorkspaceId && hackathonId) {
      loadPeople();
    }
  }, [activeWorkspaceId, hackathonId]);

  const loadPeople = async () => {
    if (!activeWorkspaceId) return;
    setIsLoading(true);
    try {
      const [mRes, jRes] = await Promise.all([
        peopleApi.getMentorAssignments(activeWorkspaceId, hackathonId),
        peopleApi.getJudgeAssignments(activeWorkspaceId, hackathonId)
      ]);
      setMentors(mRes);
      setJudges(jRes);
    } catch (error) {
      console.error("Failed to load mentors and judges", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading personnel...</div>;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <GlassPanel className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-semibold">Mentors</h2>
          </div>
          <Button size="sm">Assign Mentor</Button>
        </div>
        {mentors.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No mentors assigned to this hackathon yet.</p>
        ) : (
          <div className="space-y-2">
            {mentors.map(m => (
              <div key={m.id} className="p-3 bg-card rounded-md border flex justify-between items-center">
                <div>
                  <div className="font-medium">Mentor ID: {m.mentor_id.substring(0, 8)}...</div>
                  <div className="text-xs text-muted-foreground">Status: <span className="capitalize">{m.status}</span></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassPanel>

      <GlassPanel className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Gavel className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-semibold">Judges</h2>
          </div>
          <Button size="sm">Assign Judge</Button>
        </div>
        {judges.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No judges assigned to this hackathon yet.</p>
        ) : (
          <div className="space-y-2">
            {judges.map(j => (
              <div key={j.id} className="p-3 bg-card rounded-md border flex justify-between items-center">
                <div>
                  <div className="font-medium">Judge ID: {j.judge_id.substring(0, 8)}...</div>
                  <div className="text-xs text-muted-foreground">Status: <span className="capitalize">{j.status}</span></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassPanel>

      <div className="md:col-span-2 mt-6">
        <IntelligentResourceAllocation hackathonId={hackathonId} />
      </div>
    </div>
  );
}
