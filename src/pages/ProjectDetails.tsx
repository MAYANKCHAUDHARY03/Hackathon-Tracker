import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { GlassPanel } from "@/components/ui/glass-panel";
import { ProjectLifecycle } from "@/components/projects/ProjectLifecycle";

export default function ProjectDetails() {
  const { id } = useParams<{ id: string }>();
  const workspaceId = useWorkspaceStore((s) => s.activeWorkspaceId);
  const [projectStatus, setProjectStatus] = useState("IDEA");
  
  if (!id || !workspaceId) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Project Workspace</h1>
        <p className="text-muted-foreground mt-2">Manage your project's lifecycle, kanban, and settings.</p>
      </div>

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
    </div>
  );
}
