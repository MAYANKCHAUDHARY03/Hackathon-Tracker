import type { MatchResult } from "@/api/matchingApi";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Network } from "lucide-react";

interface GraphMatchCardProps {
  match: MatchResult;
}

export function GraphMatchCard({ match }: GraphMatchCardProps) {
  // Try to find a display name in the raw node data
  const displayName = match.data.name || match.data.title || match.data.organization_name || match.data.company_name || match.data.slug || match.node_id;

  return (
    <GlassPanel className="p-5 space-y-4 border border-border/50 relative overflow-hidden">
      {/* Graph Traversal Badge */}
      <div className="absolute top-0 right-0 bg-primary/20 text-primary text-[10px] uppercase font-bold px-2 py-1 flex items-center gap-1 rounded-bl-md">
        <Network className="h-3 w-3" /> Graph Match
      </div>

      <div className="flex justify-between items-start pt-2">
        <div>
          <h3 className="text-xl font-bold">{displayName}</h3>
          <p className="text-sm text-muted-foreground capitalize">{match.type}</p>
        </div>
        <div className="flex flex-col items-center justify-center bg-primary/10 text-primary rounded-full h-12 w-12 border border-primary/20">
          <span className="text-sm font-bold">{(match.score * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="text-sm text-muted-foreground">
        {match.data.description || match.data.bio || "No description provided."}
      </div>
      
      <div className="mt-4 pt-4 border-t border-border flex flex-wrap gap-2">
        {/* We can dump some shared properties or raw tags if any exist */}
        <span className="text-xs font-semibold px-2 py-1 rounded bg-secondary text-secondary-foreground">
          Score Based on Shared Graph Edges
        </span>
      </div>
    </GlassPanel>
  );
}
