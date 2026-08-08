import type { OpportunityMatch } from "@/api/opportunityApi";
import { GlassPanel } from "@/components/ui/glass-panel";
import { AlertCircle, CheckCircle, BrainCircuit } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

interface MatchCardProps {
  match: OpportunityMatch;
}


export function MatchCard({ match }: MatchCardProps) {
  return (
    <GlassPanel className="p-5 space-y-4 border border-border/50 relative overflow-hidden">
      {/* AI Disclaimer Badge */}
      <div className="absolute top-0 right-0 bg-secondary/80 text-secondary-foreground text-[10px] uppercase font-bold px-2 py-1 flex items-center gap-1 rounded-bl-md">
        <BrainCircuit className="h-3 w-3" /> AI-Generated Match
      </div>

      <div className="flex justify-between items-start pt-2">
        <div>
          <h3 className="text-xl font-bold">{match.target_name}</h3>
          <p className="text-sm text-muted-foreground capitalize">{match.target_type}</p>
        </div>
        <div className="flex flex-col items-center justify-center bg-primary/10 text-primary rounded-full h-12 w-12 border border-primary/20">
          <span className="text-lg font-bold">{match.score}</span>
        </div>
      </div>

      {(match.reasons || []).length > 0 && (
        <div className="space-y-1">
          <h4 className="text-sm font-semibold flex items-center gap-1">
            <CheckCircle className="h-4 w-4 text-green-500" /> Match Reasons
          </h4>
          <ul className="list-disc list-inside text-sm text-muted-foreground ml-1">
            {(match.reasons || []).map((r, idx) => (
              <li key={idx}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {(match.evidence || []).length > 0 && (
        <div className="space-y-1">
          <h4 className="text-sm font-semibold">Graph Evidence</h4>
          <ul className="list-disc list-inside text-sm text-muted-foreground ml-1">
            {(match.evidence || []).map((e, idx) => (
              <li key={idx}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Strict UI Requirement: Limitations must always be shown */}
      <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 mt-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle className="text-sm font-bold">Important Limitations</AlertTitle>
        <AlertDescription className="text-xs mt-1">
          This match is AI-generated and not a guaranteed recommendation. Consider the following:
          <ul className="list-disc list-inside mt-1">
            {(match.limitations || []).map((lim, idx) => (
              <li key={idx}>{lim}</li>
            ))}
          </ul>
        </AlertDescription>
      </Alert>
    </GlassPanel>
  );
}
