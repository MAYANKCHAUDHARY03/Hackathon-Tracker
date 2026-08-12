import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { incubationApi } from '@/api/incubationApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Lightbulb, Loader2 } from 'lucide-react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { ProjectSelector } from '@/components/incubation/ProjectSelector';
import { IncubationUpdates } from '@/components/incubation/IncubationUpdates';
import { FundingTimeline } from '@/components/incubation/FundingTimeline';
import { DocumentVault } from '@/components/incubation/DocumentVault';

export default function Incubation() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['incubation-dashboard', selectedProjectId],
    queryFn: () => incubationApi.getDashboard(selectedProjectId!),
    enabled: !!selectedProjectId
  });

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Lightbulb className="w-8 h-8 text-primary" />
            Startup Incubation
          </h1>
          <p className="text-muted-foreground text-lg">
            Track progress, manage documents, and log funding rounds for incubated projects.
          </p>
        </div>
        
        {activeWorkspaceId && (
          <div className="w-full md:w-auto">
            <ProjectSelector 
              selectedProjectId={selectedProjectId} 
              onSelectProject={setSelectedProjectId} 
            />
          </div>
        )}
      </div>

      {!activeWorkspaceId ? (
        <div className="text-center py-12 text-muted-foreground">
          Please select a workspace to view incubation projects.
        </div>
      ) : !selectedProjectId ? (
        <GlassPanel className="p-12 text-center flex flex-col items-center">
          <Lightbulb className="w-12 h-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium">Select a Project</h3>
          <p className="text-muted-foreground mt-2">
            Choose an incubated project from the dropdown above to view its dashboard.
          </p>
        </GlassPanel>
      ) : isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : dashboard ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <IncubationUpdates 
              projectId={selectedProjectId} 
              updates={dashboard.updates} 
            />
          </div>
          
          <div className="space-y-8">
            <GlassPanel className="p-6">
              <FundingTimeline 
                projectId={selectedProjectId} 
                fundingRounds={dashboard.funding_rounds} 
              />
            </GlassPanel>
            
            <GlassPanel className="p-6">
              <DocumentVault 
                projectId={selectedProjectId} 
                documents={dashboard.documents} 
              />
            </GlassPanel>
          </div>
        </div>
      ) : null}
    </div>
  );
}
