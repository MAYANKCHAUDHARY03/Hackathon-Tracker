import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { GlassPanel } from "@/components/ui/glass-panel";
import { ProjectLifecycle } from "@/components/projects/ProjectLifecycle";
import { IncubationDashboardView } from "@/components/projects/IncubationDashboard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ResearchBridge } from "@/components/research/ResearchBridge";
import { RequestVerificationModal } from "@/components/projects/RequestVerificationModal";
import { ProjectCopilot } from "@/components/projects/ProjectCopilot";
import { MentorCopilot } from "@/components/teams/MentorCopilot";
import { ProjectAgentEvaluation } from "@/components/projects/ProjectAgentEvaluation";

export default function ProjectDetails() {
  const { id } = useParams<{ id: string }>();
  const workspaceId = useWorkspaceStore((s) => s.activeWorkspaceId);
  const [projectStatus, setProjectStatus] = useState("IDEA");
  
  if (!id || !workspaceId) {
    return <div className="p-8">Loading...</div>;
  }

  const showIncubation = ["INCUBATION", "PILOT", "PRODUCTION"].includes(projectStatus);

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Project Workspace</h1>
          <p className="text-muted-foreground mt-2">Manage your project's lifecycle, kanban, and settings.</p>
        </div>
        <RequestVerificationModal workspaceId={workspaceId} projectId={id} />
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="copilot">Project Copilot</TabsTrigger>
          <TabsTrigger value="mentor-copilot">Mentor Brief</TabsTrigger>
          <TabsTrigger value="evaluations">Evaluations (AI)</TabsTrigger>
          <TabsTrigger value="research">Research Bridge</TabsTrigger>
          {showIncubation && <TabsTrigger value="incubation">Incubation & Acceleration</TabsTrigger>}
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <GlassPanel className="p-6">
              <h2 className="text-xl font-semibold mb-6">Lifecycle State</h2>
              <ProjectLifecycle 
                workspaceId={workspaceId} 
                projectId={id} 
                currentStatus={projectStatus} 
                onStatusChange={setProjectStatus} 
              />
            </GlassPanel>
            
            <GlassPanel className="p-6 flex items-center justify-center text-muted-foreground border-dashed">
              Future: Kanban and Team View
            </GlassPanel>
          </div>
        </TabsContent>

        <TabsContent value="copilot" className="space-y-6">
          <ProjectCopilot projectId={id} workspaceId={workspaceId} />
        </TabsContent>

        <TabsContent value="mentor-copilot" className="space-y-6">
          <MentorCopilot projectId={id} workspaceId={workspaceId} />
        </TabsContent>

        <TabsContent value="research" className="space-y-6">
          <GlassPanel className="p-6">
            <h2 className="text-xl font-semibold mb-6">Research Bridge</h2>
            <p className="text-muted-foreground mb-6">Link this project to external research artifacts like papers, datasets, and patents.</p>
            <ResearchBridge projectId={id} />
          </GlassPanel>
        </TabsContent>

        <TabsContent value="evaluations" className="space-y-6">
          <ProjectAgentEvaluation projectId={id} workspaceId={workspaceId} />
        </TabsContent>

        {showIncubation && (
          <TabsContent value="incubation" className="mt-0">
            <IncubationDashboardView projectId={id} />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}
