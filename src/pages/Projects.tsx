import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { projectsApi } from '@/api/projectsApi';
import type { Project } from '@/types';
import { hackathonApi } from '@/api/hackathonApi';
import { teamApi } from '@/api/teamApi';
import type { Hackathon } from '@/types';
import type { Team } from '@/api/teamApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { FolderGit2, Calendar, GitBranch, ArrowRight, Plus } from 'lucide-react';
import { format } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function Projects() {
  const navigate = useNavigate();
  const { activeWorkspaceId, applicationMode } = useWorkspaceStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '', hackathon_id: '', team_id: '' });
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);

  useEffect(() => {
    async function fetchProjects() {
      if (!activeWorkspaceId) return;
      setIsLoading(true);
      setError(null);
      try {
        const [projData, hackData, teamData] = await Promise.all([
          projectsApi.getProjects(activeWorkspaceId),
          hackathonApi.getHackathons(activeWorkspaceId),
          teamApi.getTeams(activeWorkspaceId)
        ]);
        const pList = Array.isArray(projData) ? projData : Array.isArray((projData as any)?.items) ? (projData as any).items : Array.isArray((projData as any)?.data) ? (projData as any).data : [];
        setProjects(pList);

        const hList = Array.isArray(hackData) ? hackData : Array.isArray((hackData as any)?.items) ? (hackData as any).items : Array.isArray((hackData as any)?.data) ? (hackData as any).data : [];
        setHackathons(hList);

        const tList = Array.isArray(teamData) ? teamData : Array.isArray((teamData as any)?.items) ? (teamData as any).items : Array.isArray((teamData as any)?.data) ? (teamData as any).data : [];
        setTeams(tList);
      } catch (err: any) {
        setError(err instanceof Error ? err : new Error('Failed to load projects'));
      } finally {
        setIsLoading(false);
      }
    }
    fetchProjects();
  }, [activeWorkspaceId]);

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId) return;
    if (!newProject.hackathon_id || !newProject.team_id) {
       toast.error("Hackathon and Team are required.");
       return;
    }
    try {
      setIsSubmitting(true);
      const created = await projectsApi.createProject(activeWorkspaceId, newProject.team_id, {
        name: newProject.name,
        description: newProject.description,
        hackathon_id: newProject.hackathon_id
      } as any);
      setProjects(prev => [...prev, created]);
      setIsDialogOpen(false);
      setNewProject({ name: '', description: '', hackathon_id: '', team_id: '' });
      toast.success("Project created successfully");
    } catch (err: any) {
      toast.error(err.message || 'Failed to create project');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredTeams = teams.filter(t => t.hackathon_id === newProject.hackathon_id);

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Project Database</h1>
          <p className="text-muted-foreground mt-1">Explore projects submitted across the workspace.</p>
        </div>
        {applicationMode === 'student' && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Create Project
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Create a New Project</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateProject} className="space-y-4 pt-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Project Name</label>
                  <input
                    name="name"
                    required
                    type="text"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={newProject.name}
                    onChange={e => setNewProject({...newProject, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Hackathon</label>
                  <select
                    name="hackathon_id"
                    required
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={newProject.hackathon_id}
                    onChange={e => setNewProject({...newProject, hackathon_id: e.target.value, team_id: ''})}
                  >
                    <option value="" disabled>Select a Hackathon</option>
                    {hackathons.map(h => (
                      <option key={h.id} value={h.id}>{h.name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Team</label>
                  <select
                    name="team_id"
                    required
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={newProject.team_id}
                    onChange={e => setNewProject({...newProject, team_id: e.target.value})}
                    disabled={!newProject.hackathon_id}
                  >
                    <option value="" disabled>Select a Team</option>
                    {filteredTeams.map(t => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <textarea
                    name="description"
                    required
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={newProject.description}
                    onChange={e => setNewProject({...newProject, description: e.target.value})}
                  />
                </div>
                <div className="flex justify-end gap-3 mt-6">
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)} disabled={isSubmitting}>Cancel</Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Creating...' : 'Create Project'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map(i => (
            <GlassPanel key={i} className="h-48 animate-pulse bg-secondary/20" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center p-8 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
          <p>{error.message}</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-12">
          <div className="p-4 bg-primary/10 text-primary rounded-full w-16 h-16 mx-auto flex items-center justify-center mb-4">
            <FolderGit2 className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-semibold mb-2">No projects found</h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Projects will appear here once teams create submissions.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map(project => (
            <GlassPanel 
              key={project.id} 
              className="p-6 flex flex-col hover:border-primary/50 transition-all cursor-pointer group hover:shadow-md"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold truncate pr-4 group-hover:text-primary transition-colors">
                  {project.name}
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-secondary text-secondary-foreground px-2 py-1 rounded">
                  {(project as any).status || 'Active'}
                </span>
              </div>
              
              <p className="text-sm text-muted-foreground line-clamp-3 mb-6 flex-1">
                {project.description || 'No description provided.'}
              </p>
              
              <div className="space-y-2 mb-4">
                {project.github_repo_url && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <GitBranch className="h-4 w-4" />
                    <span className="truncate">{(() => { try { return new URL(project.github_repo_url!).hostname; } catch { return project.github_repo_url; } })()}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Updated {format(new Date(project.updated_at), 'MMM d, yyyy')}</span>
                </div>
              </div>
              
              <div className="mt-auto pt-4 border-t border-border/50 flex items-center justify-between text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                <span>View Details</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
