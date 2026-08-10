import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { portfolioApi, type OrganizationPortfolio } from "@/api/portfolioApi";
import { 
  Building2, Loader2, Target, Rocket, Lightbulb, 
  CheckCircle, Briefcase, ChevronRight 
} from "lucide-react";

export default function OrgPortfolio() {
  const { orgId } = useParams<{ orgId: string }>();
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const [portfolio, setPortfolio] = useState<OrganizationPortfolio | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orgId || !workspaceId) return;
    
    setLoading(true);
    portfolioApi.getOrganizationPortfolio(workspaceId, orgId)
      .then(res => setPortfolio(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [orgId, workspaceId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground animate-pulse">Aggregating graph-sourced portfolio data...</p>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Failed to load organization portfolio.</p>
      </div>
    );
  }

  const { stats, projects, startups } = portfolio;

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl space-y-8 animate-fade-in">
      <div className="flex items-center gap-4 pb-6 border-b border-border">
        <div className="h-16 w-16 bg-primary/10 rounded-xl flex items-center justify-center border border-primary/20">
          <Building2 className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">{portfolio.name}</h1>
          <p className="text-muted-foreground">Innovation Portfolio Summary</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-6 bg-card border border-border rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Total Projects</h3>
            <Briefcase className="h-5 w-5 text-primary" />
          </div>
          <p className="text-3xl font-bold">{stats.total_projects}</p>
          <div className="text-sm text-muted-foreground mt-2 flex gap-2">
            <span className="flex items-center"><Target className="h-3 w-3 mr-1"/> {stats.active_projects} Active</span>
            <span className="flex items-center"><CheckCircle className="h-3 w-3 mr-1"/> {stats.completed_projects} Done</span>
          </div>
        </div>

        <div className="p-6 bg-card border border-border rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Startups Spawned</h3>
            <Rocket className="h-5 w-5 text-primary" />
          </div>
          <p className="text-3xl font-bold">{stats.startups_spawned}</p>
        </div>

        <div className="p-6 bg-card border border-border rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Patents & Research</h3>
            <Lightbulb className="h-5 w-5 text-primary" />
          </div>
          <p className="text-3xl font-bold">{stats.patents_research}</p>
        </div>

        <div className="p-6 bg-card border border-border rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Top Technologies</h3>
            <Target className="h-5 w-5 text-primary" />
          </div>
          <div className="flex flex-wrap gap-2">
            {stats.top_technologies.map(tech => (
              <span key={tech} className="text-xs bg-secondary px-2 py-1 rounded-md border border-border/50">{tech}</span>
            ))}
            {stats.top_technologies.length === 0 && <span className="text-xs text-muted-foreground">No data</span>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Notable Projects</h2>
          <div className="space-y-4">
            {projects.slice(0, 5).map(proj => (
              <div key={proj.id} className="p-4 bg-card/50 border border-border rounded-lg hover:bg-card transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold">{proj.name}</h4>
                  <span className="text-xs px-2 py-1 bg-secondary rounded-full border border-border/50">{proj.status}</span>
                </div>
                {proj.description && <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{proj.description}</p>}
                <div className="flex flex-wrap gap-1">
                  {proj.technologies.slice(0, 3).map(tech => (
                    <span key={tech} className="text-[10px] bg-background px-1.5 py-0.5 rounded border border-border/50">{tech}</span>
                  ))}
                  {proj.technologies.length > 3 && <span className="text-[10px] text-muted-foreground">+{proj.technologies.length - 3}</span>}
                </div>
              </div>
            ))}
            {projects.length === 0 && <p className="text-sm text-muted-foreground text-center py-8">No projects tracked yet.</p>}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Spinoff Startups</h2>
          <div className="space-y-4">
            {startups.map(startup => (
              <div key={startup.id} className="p-4 bg-card/50 border border-border rounded-lg flex items-center justify-between hover:bg-card transition-colors">
                <div>
                  <h4 className="font-bold flex items-center gap-2">
                    <Rocket className="h-4 w-4 text-primary" /> {startup.name}
                  </h4>
                  {startup.description && <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{startup.description}</p>}
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </div>
            ))}
            {startups.length === 0 && <p className="text-sm text-muted-foreground text-center py-8">No startups spawned yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
