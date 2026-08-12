import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '@/api/projectsApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { FolderGit2, Search, Link as LinkIcon, GitBranch, ChevronRight, Loader2 } from 'lucide-react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';

export default function Projects() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', activeWorkspaceId],
    queryFn: () => projectsApi.getProjects(activeWorkspaceId!),
    enabled: !!activeWorkspaceId
  });

  const filteredProjects = projects?.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    p.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!activeWorkspaceId) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-muted-foreground">
        Please select a workspace to view projects.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <FolderGit2 className="w-8 h-8 text-primary" />
            Project Database
          </h1>
          <p className="text-muted-foreground text-lg mt-1">
            Explore and track all hackathon projects in your workspace.
          </p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input 
          placeholder="Search projects..." 
          className="pl-9"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : filteredProjects?.length === 0 ? (
        <GlassPanel className="p-12 text-center flex flex-col items-center">
          <FolderGit2 className="w-12 h-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium">No Projects Found</h3>
          <p className="text-muted-foreground mt-2">
            Try adjusting your search query.
          </p>
        </GlassPanel>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProjects?.map(project => (
            <Link key={project.id} to={`/projects/${project.id}`} className="group block">
              <GlassPanel className="p-6 flex flex-col h-full hover:bg-secondary/20 transition-all border border-border/50 hover:border-primary/50 relative overflow-hidden">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-bold text-xl group-hover:text-primary transition-colors pr-8">
                    {project.name}
                  </h3>
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors absolute right-6 top-6" />
                </div>
                
                <p className="text-sm text-muted-foreground line-clamp-3 mb-6 flex-1">
                  {project.description || 'No description provided.'}
                </p>

                <div className="flex flex-wrap gap-3 pt-4 border-t border-border/50 mt-auto">
                  {project.github_repo_url && (
                    <div className="flex items-center text-xs text-muted-foreground bg-secondary/50 px-2 py-1 rounded">
                      <GitBranch className="w-3 h-3 mr-1" />
                      Repo Link
                    </div>
                  )}
                  {project.demo_url && (
                    <div className="flex items-center text-xs text-muted-foreground bg-secondary/50 px-2 py-1 rounded">
                      <LinkIcon className="w-3 h-3 mr-1" />
                      Demo Link
                    </div>
                  )}
                  {!project.github_repo_url && !project.demo_url && (
                    <div className="text-xs text-muted-foreground italic">
                      No links provided
                    </div>
                  )}
                </div>
              </GlassPanel>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
