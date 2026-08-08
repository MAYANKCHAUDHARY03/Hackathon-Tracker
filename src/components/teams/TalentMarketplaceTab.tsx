import { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { teamApi, Team, TalentMatch } from '@/api/teamApi';
import { peopleApi, Person } from '@/api/people';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Users, Search, Target, UserPlus } from 'lucide-react';

export function TalentMarketplaceTab({ hackathonId }: { hackathonId: string }) {
  const currentWorkspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const [teams, setTeams] = useState<Team[]>([]);
  const [people, setPeople] = useState<Person[]>([]);
  const [matches, setMatches] = useState<Record<string, TalentMatch[]>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (currentWorkspaceId) {
      loadData();
    }
  }, [currentWorkspaceId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const fetchedTeams = await teamApi.getTeams(currentWorkspaceId!);
      // Only show teams for this hackathon
      setTeams(fetchedTeams.filter(t => t.hackathon_id === hackathonId));
      
      const fetchedPeople = await peopleApi.getPeople(currentWorkspaceId!);
      setPeople(fetchedPeople);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async (teamId: string) => {
    if (!currentWorkspaceId) return;
    try {
      const result = await teamApi.getTalentMatches(currentWorkspaceId, teamId);
      setMatches(prev => ({ ...prev, [teamId]: result }));
    } catch (err) {
      console.error(err);
    }
  };

  const handleApply = async (teamId: string) => {
    if (!currentWorkspaceId) return;
    try {
      await teamApi.applyToTeam(currentWorkspaceId, teamId);
      alert('Applied to team successfully!');
    } catch (err) {
      console.error(err);
      alert('Failed to apply. Do you have a person profile?');
    }
  };

  const handleInvite = async (teamId: string, personId: string) => {
    if (!currentWorkspaceId) return;
    try {
      await teamApi.inviteToTeam(currentWorkspaceId, teamId, personId);
      alert('Invited talent to team successfully!');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Users className="h-5 w-5" /> Talent Marketplace
        </h2>
        <Button onClick={loadData} disabled={loading} variant="outline" size="sm">
          Refresh
        </Button>
      </div>
      
      <div className="grid md:grid-cols-2 gap-6">
        {/* Teams Looking for Talent */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2">Teams Looking for Talent</h3>
          {teams.length === 0 && <p className="text-muted-foreground text-sm">No teams found.</p>}
          {teams.map(team => (
            <GlassPanel key={team.id} className="p-4 space-y-3 relative overflow-hidden group">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-lg">{team.name}</h4>
                  {team.description && <p className="text-sm text-muted-foreground">{team.description}</p>}
                </div>
                <Button size="sm" variant="secondary" onClick={() => handleApply(team.id)}>
                  Apply
                </Button>
              </div>
              
              <div className="pt-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">Skills Needed:</p>
                <div className="flex flex-wrap gap-1">
                  {team.skills_needed && team.skills_needed.length > 0 ? (
                    team.skills_needed.map((skill, idx) => (
                      <span key={idx} className="bg-primary/10 text-primary text-xs px-2 py-1 rounded-full border border-primary/20">
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-muted-foreground italic">None specified</span>
                  )}
                </div>
              </div>

              <div className="pt-3 border-t border-border/50">
                <Button size="sm" variant="ghost" className="w-full justify-between" onClick={() => handleMatch(team.id)}>
                  <span className="flex items-center gap-2"><Target className="h-4 w-4" /> Find Matches via AI</span>
                </Button>
                
                {matches[team.id] && (
                  <div className="mt-3 space-y-2 bg-black/20 p-3 rounded-md">
                    <p className="text-xs font-semibold text-muted-foreground">AI Recommended Talent:</p>
                    {matches[team.id].length === 0 ? (
                      <p className="text-xs text-muted-foreground">No matches found.</p>
                    ) : (
                      matches[team.id].map(match => (
                        <div key={match.person_id} className="flex justify-between items-center bg-card p-2 rounded border border-border/50 text-sm">
                          <div>
                            <span className="font-medium">{match.full_name}</span>
                            <span className="text-xs text-green-400 ml-2">Score: {match.match_score}</span>
                          </div>
                          <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => handleInvite(team.id, match.person_id)} title="Invite">
                            <UserPlus className="h-4 w-4" />
                          </Button>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </GlassPanel>
          ))}
        </div>

        {/* Talent Looking for Teams */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2">Talent Pool</h3>
          {people.length === 0 && <p className="text-muted-foreground text-sm">No talent found.</p>}
          <div className="grid gap-3">
            {people.map(person => (
              <GlassPanel key={person.id} className="p-4 flex items-center justify-between">
                <div>
                  <h4 className="font-semibold">{person.first_name} {person.last_name}</h4>
                  {person.bio && <p className="text-xs text-muted-foreground">{person.bio}</p>}
                  
                  {/* Assuming expertise_areas exists in Person backend but might not be in the frontend Person type completely. Let's cast or check. */}
                  {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                  {(person as any).expertise_areas && ((person as any).expertise_areas as string[]).length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                      {((person as any).expertise_areas as string[]).map((skill, idx) => (
                        <span key={idx} className="bg-secondary text-secondary-foreground text-xs px-2 py-0.5 rounded border border-secondary/20">
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </GlassPanel>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
