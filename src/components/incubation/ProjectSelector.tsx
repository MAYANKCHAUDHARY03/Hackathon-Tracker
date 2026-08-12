import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { projectsApi } from '@/api/projectsApi';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';

interface ProjectSelectorProps {
  selectedProjectId: string | null;
  onSelectProject: (projectId: string) => void;
}

export function ProjectSelector({ selectedProjectId, onSelectProject }: ProjectSelectorProps) {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);

  const { data: projects, isLoading } = useQuery({
    queryKey: ['workspace-projects', workspaceId],
    queryFn: () => projectsApi.getProjects(workspaceId!),
    enabled: !!workspaceId
  });

  return (
    <div className="w-full max-w-sm">
      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading projects...
        </div>
      ) : (
        <Select 
          value={selectedProjectId || undefined} 
          onValueChange={onSelectProject}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select an incubated project" />
          </SelectTrigger>
          <SelectContent>
            {projects?.map(project => (
              <SelectItem key={project.id} value={project.id}>
                {project.name}
              </SelectItem>
            ))}
            {projects?.length === 0 && (
              <div className="p-2 text-sm text-muted-foreground text-center">
                No projects found.
              </div>
            )}
          </SelectContent>
        </Select>
      )}
    </div>
  );
}
