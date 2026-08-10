import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, FileText, Target, Users, DollarSign, TrendingUp, Plus, ExternalLink } from "lucide-react";
import { format } from 'date-fns';
import { incubationApi } from '@/api/incubationApi';
import type { IncubationDashboard, ProjectUpdate, ProjectDocument, ProjectFunding, Stakeholder } from '@/api/incubationApi';

export function IncubationDashboardView({ projectId }: { projectId: string }) {
  const [data, setData] = useState<IncubationDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [projectId]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const dashboardData = await incubationApi.getDashboard(projectId);
      setData(dashboardData);
    } catch (error) {
      console.error("Failed to load incubation dashboard", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading incubation data...</div>;
  if (!data) return <div className="p-8 text-center text-muted-foreground">Failed to load incubation dashboard.</div>;

  return (
    <div className="space-y-6">
      
      {/* Top Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-4 w-4 text-primary" />
              <h3 className="font-medium">Total Funding</h3>
            </div>
            <p className="text-2xl font-bold mt-2">
              ${data.funding_rounds.reduce((sum, round) => sum + round.amount, 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4 text-blue-500" />
              <h3 className="font-medium">Milestones</h3>
            </div>
            <p className="text-2xl font-bold mt-2">
              {data.updates.filter(u => u.update_type === 'kpi').length} Completed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-green-500" />
              <h3 className="font-medium">Stakeholders</h3>
            </div>
            <p className="text-2xl font-bold mt-2">{data.stakeholders.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-amber-500" />
              <h3 className="font-medium">Documents</h3>
            </div>
            <p className="text-2xl font-bold mt-2">{data.documents.length}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Timeline & Updates */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Updates & Progress</CardTitle>
                <CardDescription>Recent progress reports and KPI updates</CardDescription>
              </div>
              <Button size="sm"><Plus className="h-4 w-4 mr-2" /> New Update</Button>
            </CardHeader>
            <CardContent>
              {data.updates.length === 0 ? (
                <div className="text-center p-6 text-muted-foreground border border-dashed rounded-md">
                  No updates posted yet. Keep your stakeholders informed!
                </div>
              ) : (
                <div className="space-y-6">
                  {data.updates.map(update => (
                    <div key={update.id} className="relative pl-6 border-l-2 border-primary/20 pb-4 last:border-0">
                      <div className="absolute w-3 h-3 bg-primary rounded-full -left-[7px] top-1" />
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-semibold">{update.title}</h4>
                          <Badge variant="outline" className="text-xs">
                            {update.update_type.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                        <span className="text-xs text-muted-foreground flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          {format(new Date(update.created_at), 'MMM d, yyyy')}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">{update.content}</p>
                      
                      {update.kpi_metrics && Object.keys(update.kpi_metrics).length > 0 && (
                        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.entries(update.kpi_metrics).map(([key, value]) => (
                            <div key={key} className="bg-muted p-2 rounded-md text-center">
                              <div className="text-xs text-muted-foreground uppercase">{key.replace('_', ' ')}</div>
                              <div className="font-semibold">{String(value)}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Stakeholders, Funding, Docs */}
        <div className="space-y-6">
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Funding History</CardTitle>
            </CardHeader>
            <CardContent>
              {data.funding_rounds.length === 0 ? (
                <p className="text-sm text-muted-foreground">No funding rounds recorded.</p>
              ) : (
                <div className="space-y-4">
                  {data.funding_rounds.map(round => (
                    <div key={round.id} className="flex justify-between items-center border-b pb-2 last:border-0">
                      <div>
                        <div className="font-medium">{round.round_type.replace('_', ' ').toUpperCase()}</div>
                        <div className="text-xs text-muted-foreground">{format(new Date(round.date), 'MMM yyyy')}</div>
                      </div>
                      <div className="font-bold text-primary">
                        {round.amount.toLocaleString()} {round.currency}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg">Documents</CardTitle>
                <Button variant="ghost" size="icon" className="h-6 w-6"><Plus className="h-4 w-4" /></Button>
              </div>
            </CardHeader>
            <CardContent>
              {data.documents.length === 0 ? (
                <p className="text-sm text-muted-foreground">No documents uploaded.</p>
              ) : (
                <div className="space-y-2">
                  {data.documents.map(doc => (
                    <a key={doc.id} href={doc.url} target="_blank" rel="noreferrer" className="flex items-center justify-between p-2 hover:bg-muted rounded-md group transition-colors">
                      <div className="flex items-center space-x-2 truncate">
                        <FileText className="h-4 w-4 text-muted-foreground group-hover:text-primary flex-shrink-0" />
                        <span className="text-sm truncate">{doc.title}</span>
                      </div>
                      <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 text-muted-foreground" />
                    </a>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Stakeholders & Advisors</CardTitle>
            </CardHeader>
            <CardContent>
              {data.stakeholders.length === 0 ? (
                <p className="text-sm text-muted-foreground">No stakeholders added.</p>
              ) : (
                <div className="space-y-3">
                  {data.stakeholders.map(person => (
                    <div key={person.user_id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium text-xs">
                          {person.name.charAt(0)}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{person.name}</p>
                          <p className="text-xs text-muted-foreground">{person.role.replace('_', ' ')}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
