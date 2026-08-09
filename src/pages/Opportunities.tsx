import { useState, useEffect } from "react";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { useAuthStore } from "@/store/authStore";
import { peopleApi } from "@/api/people";
import type { Person } from "@/api/people";
import { matchingApi } from "@/api/matchingApi";
import type { MatchResult } from "@/api/matchingApi";
import { GraphMatchCard } from "@/components/opportunities/GraphMatchCard";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Sparkles, Loader2 } from "lucide-react";

export default function Opportunities() {
  const currentWorkspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const user = useAuthStore(s => s.user);
  
  const [person, setPerson] = useState<Person | null>(null);
  const [targetType, setTargetType] = useState<string>("Hackathon");
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    // Attempt to find the Person profile for the logged in user
    const fetchPerson = async () => {
      if (!currentWorkspaceId || !user) return;
      try {
        const peopleList = await peopleApi.getPeople(currentWorkspaceId);
        const myProfile = peopleList.find(p => p.email === user.email);
        if (myProfile) {
          setPerson(myProfile);
        }
      } catch (err) {
        console.error("Could not fetch person profile", err);
      }
    };
    fetchPerson();
  }, [currentWorkspaceId, user]);

  const handleMatch = async () => {
    if (!currentWorkspaceId || !person) return;
    try {
      setLoading(true);
      setHasSearched(true);
      const res = await matchingApi.findMatches(
        currentWorkspaceId,
        person.id,
        targetType
      );
      setMatches(res || []);
    } catch (err) {
      console.error(err);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary" /> Opportunity Discovery
          </h1>
          <p className="text-muted-foreground mt-1">
            Discover graph-backed, AI-scored opportunities matching your profile.
          </p>
        </div>
      </div>

      {!person ? (
        <div className="text-center py-12 bg-secondary/20 rounded-xl border border-border">
          <p className="text-muted-foreground">You must have a Person profile in this workspace to discover opportunities.</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-end gap-4 p-4 bg-card border border-border rounded-lg">
            <div className="space-y-1 flex-1">
              <label className="text-sm font-medium">I am looking for...</label>
              <Select value={targetType} onValueChange={setTargetType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select target type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Hackathon">Hackathons</SelectItem>
                  <SelectItem value="Team">Teams</SelectItem>
                  <SelectItem value="Project">Projects to Join</SelectItem>
                  <SelectItem value="Organization">Organizations</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleMatch} disabled={loading} className="w-32">
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
              Find Matches
            </Button>
          </div>

          <div className="grid gap-6">
            {loading && (
              <div className="py-12 flex flex-col items-center justify-center space-y-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-muted-foreground animate-pulse">Traversing the Innovation Graph...</p>
              </div>
            )}
            
            {!loading && hasSearched && matches.length === 0 && (
              <div className="text-center py-12 border border-border rounded-lg bg-card/50">
                <p className="text-muted-foreground">No strong matches found for {targetType} right now.</p>
              </div>
            )}

            {!loading && matches.map(match => (
              <GraphMatchCard key={match.node_id} match={match} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
