import { useState, useEffect } from "react";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { outcomesApi } from "@/api/outcomes";
import type { HackathonResult, Reward, Achievement } from "@/api/outcomes";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Button } from "@/components/ui/button";
import { Trophy, Gift, Medal } from "lucide-react";

interface OutcomesTabProps {
  hackathonId: string;
}

export function OutcomesTab({ hackathonId }: OutcomesTabProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [results, setResults] = useState<HackathonResult[]>([]);
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (activeWorkspaceId && hackathonId) {
      loadOutcomes();
    }
  }, [activeWorkspaceId, hackathonId]);

  const loadOutcomes = async () => {
    if (!activeWorkspaceId) return;
    setIsLoading(true);
    try {
      const [resRes, rewRes, achRes] = await Promise.all([
        outcomesApi.getResults(activeWorkspaceId, hackathonId),
        outcomesApi.getRewards(activeWorkspaceId, hackathonId),
        outcomesApi.getAchievements(activeWorkspaceId, hackathonId)
      ]);
      setResults(resRes);
      setRewards(rewRes);
      setAchievements(achRes);
    } catch (error) {
      console.error("Failed to load outcomes", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading outcomes...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Results */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            <h2 className="text-xl font-semibold">Results</h2>
          </div>
          <Button size="sm">Publish Result</Button>
        </div>
        
        {results.length === 0 ? (
          <GlassPanel className="p-8 text-center border-dashed">
            <p className="text-muted-foreground">No results published yet.</p>
          </GlassPanel>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {results.map(r => (
              <GlassPanel key={r.id} className="p-5 border-l-4 border-l-amber-500">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="inline-flex items-center rounded-full bg-amber-500/10 px-2 py-1 text-xs font-medium text-amber-500 capitalize mb-2">
                      {r.result_type.replace('_', ' ')}
                    </span>
                    <h3 className="font-semibold">{r.title}</h3>
                  </div>
                  {r.position && <span className="font-bold text-2xl text-muted-foreground/30">#{r.position}</span>}
                </div>
                {r.description && <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{r.description}</p>}
              </GlassPanel>
            ))}
          </div>
        )}
      </section>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Rewards */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Gift className="h-5 w-5 text-emerald-500" />
              <h2 className="text-xl font-semibold">Rewards</h2>
            </div>
            <Button size="sm" variant="outline">Add Reward</Button>
          </div>
          
          {rewards.length === 0 ? (
            <GlassPanel className="p-8 text-center border-dashed">
              <p className="text-sm text-muted-foreground">No rewards allocated yet.</p>
            </GlassPanel>
          ) : (
            <div className="space-y-3">
              {rewards.map(r => (
                <GlassPanel key={r.id} className="p-4 flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">{r.title}</h4>
                    <p className="text-xs text-muted-foreground capitalize">{r.reward_type}</p>
                  </div>
                  {r.monetary_value && (
                    <div className="font-semibold text-emerald-500">
                      {r.currency} {r.monetary_value}
                    </div>
                  )}
                </GlassPanel>
              ))}
            </div>
          )}
        </section>

        {/* Achievements */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Medal className="h-5 w-5 text-purple-500" />
              <h2 className="text-xl font-semibold">Achievements</h2>
            </div>
            <Button size="sm" variant="outline">Grant Badge</Button>
          </div>
          
          {achievements.length === 0 ? (
            <GlassPanel className="p-8 text-center border-dashed">
              <p className="text-sm text-muted-foreground">No achievements granted yet.</p>
            </GlassPanel>
          ) : (
            <div className="space-y-3">
              {achievements.map(a => (
                <GlassPanel key={a.id} className="p-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-purple-500/10 flex items-center justify-center shrink-0">
                    <Medal className="h-5 w-5 text-purple-500" />
                  </div>
                  <div>
                    <h4 className="font-medium text-sm">{a.title}</h4>
                    {a.description && <p className="text-xs text-muted-foreground truncate">{a.description}</p>}
                  </div>
                </GlassPanel>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
