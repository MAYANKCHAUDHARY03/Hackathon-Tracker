import React, { useState, useEffect } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { Banknote, TrendingUp, CheckCircle, XCircle } from 'lucide-react';

interface FundingOpportunity {
  id: string;
  title: string;
  opportunity_type: string;
  amount: number | null;
  currency: string;
  sponsor_name: string;
  description: string;
}

interface OpportunityMatch {
  opportunity: FundingOpportunity;
  match_score: number;
  matched_criteria: string[];
  missing_criteria: string[];
}

export default function FinancingIntelligence() {
  const [matches, setMatches] = useState<OpportunityMatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const response = await apiClient.get<OpportunityMatch[]>('/financing/matches/me');
        setMatches(response);
      } catch (err) {
        console.error('Failed to load funding matches', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMatches();
  }, []);

  if (loading) {
    return <div className="p-8 text-center animate-pulse">Scanning Innovation Ecosystem for Funding...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-6">
      <div className="flex justify-between items-center border-b border-border/50 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Banknote className="h-6 w-6 text-primary" /> Innovation Financing Intelligence
          </h1>
          <p className="text-muted-foreground mt-1">Discover grants, accelerators, and funding matched to your verified credentials.</p>
        </div>
      </div>

      <div className="grid gap-6">
        {matches.length === 0 ? (
          <GlassPanel className="p-8 text-center text-muted-foreground">
            No strong matches found based on your current verified skills and achievements.
            Verify more claims in your Innovation Passport to unlock opportunities.
          </GlassPanel>
        ) : (
          matches.map(match => (
            <GlassPanel key={match.opportunity.id} className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    {match.opportunity.title}
                  </h2>
                  <div className="text-sm text-muted-foreground flex items-center gap-2 mt-1">
                    <span className="bg-primary/10 text-primary px-2 py-0.5 rounded text-xs">{match.opportunity.opportunity_type}</span>
                    <span>Sponsored by {match.opportunity.sponsor_name}</span>
                  </div>
                </div>
                {match.opportunity.amount && (
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-500">
                      {match.opportunity.amount.toLocaleString()} {match.opportunity.currency}
                    </div>
                  </div>
                )}
              </div>
              
              <p className="mt-4 text-sm">{match.opportunity.description}</p>
              
              <div className="mt-6 border-t border-border/50 pt-4 grid md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-semibold mb-2">Match Score: {Math.round(match.match_score * 100)}%</h3>
                  {match.matched_criteria.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground mb-1">Verified Strengths</div>
                      {match.matched_criteria.map(c => (
                        <div key={c} className="text-xs flex items-center gap-1 text-green-500">
                          <CheckCircle className="h-3 w-3" /> {c}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                <div>
                  {match.missing_criteria.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground mb-1">Missing Requirements</div>
                      {match.missing_criteria.map(c => (
                        <div key={c} className="text-xs flex items-center gap-1 text-red-500">
                          <XCircle className="h-3 w-3" /> {c}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="mt-4">
                    <Button size="sm" variant={match.missing_criteria.length > 0 ? "secondary" : "default"} className="w-full">
                      {match.missing_criteria.length > 0 ? "Verify Missing Criteria" : "Apply Now"}
                    </Button>
                  </div>
                </div>
              </div>
            </GlassPanel>
          ))
        )}
      </div>
    </div>
  );
}
