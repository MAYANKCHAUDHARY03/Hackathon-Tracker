import { useEffect, useState } from 'react';
import { portfolioApi, type WorkspacePortfolioMetrics } from '@/api/portfolioApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Briefcase, Activity, CheckCircle, Rocket, FileText, Users, Code } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function WorkspacePortfolio() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [metrics, setMetrics] = useState<WorkspacePortfolioMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspaceId) return;

    const fetchPortfolio = async () => {
      try {
        const response = await portfolioApi.getWorkspacePortfolio(activeWorkspaceId);
        setMetrics(response);
      } catch (error) {
        console.error('Failed to load portfolio metrics', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [activeWorkspaceId]);

  if (loading || !metrics) {
    return (
      <div className="space-y-6 animate-pulse max-w-7xl mx-auto">
        <div>
          <div className="h-10 w-64 bg-muted rounded"></div>
          <div className="h-5 w-96 bg-muted mt-2 rounded"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-card rounded-xl border border-border"></div>
          ))}
        </div>
        <div className="h-64 bg-card rounded-xl border border-border mt-6"></div>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Projects', value: metrics.total_projects, icon: Briefcase, color: 'text-blue-500' },
    { label: 'Active Projects', value: metrics.active_projects, icon: Activity, color: 'text-amber-500' },
    { label: 'Completed Projects', value: metrics.completed_projects, icon: CheckCircle, color: 'text-green-500' },
    { label: 'Total Participants', value: metrics.total_participants, icon: Users, color: 'text-purple-500' },
  ];

  const chartData = metrics.top_technologies.map(t => ({
    name: t.name,
    Projects: t.count
  }));

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto">
      <div>
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent pb-1">
          Innovation Portfolio
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Track organization-wide innovation outcomes, startups, and technology adoption.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, i) => (
          <div key={i} className="p-6 glass-panel rounded-2xl flex flex-col justify-between hover-lift">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground font-medium">{stat.label}</span>
              <stat.icon className={`h-6 w-6 ${stat.color} opacity-80`} />
            </div>
            <div className="text-4xl font-extrabold mt-4">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 p-6 glass-panel rounded-2xl">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Code className="h-5 w-5 text-primary" />
            Top Technologies Used
          </h2>
          <div className="h-80">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis 
                    dataKey="name" 
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip 
                    cursor={{fill: 'hsl(var(--muted)/0.5)'}}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      borderColor: 'hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="Projects" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                No technology data available yet.
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="p-6 glass-panel rounded-2xl hover-lift bg-gradient-to-br from-card to-card/50">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-1">Startups Spawned</h3>
                <p className="text-sm text-muted-foreground">New ventures originating from hackathons</p>
              </div>
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <Rocket className="h-6 w-6 text-blue-500" />
              </div>
            </div>
            <div className="mt-6 text-5xl font-black bg-gradient-to-r from-blue-500 to-blue-400 bg-clip-text text-transparent">
              {metrics.startups_spawned}
            </div>
          </div>

          <div className="p-6 glass-panel rounded-2xl hover-lift bg-gradient-to-br from-card to-card/50">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-1">Patents Filed</h3>
                <p className="text-sm text-muted-foreground">Intellectual property generated</p>
              </div>
              <div className="p-3 bg-purple-500/10 rounded-xl">
                <FileText className="h-6 w-6 text-purple-500" />
              </div>
            </div>
            <div className="mt-6 text-5xl font-black bg-gradient-to-r from-purple-500 to-purple-400 bg-clip-text text-transparent">
              {metrics.patents_filed}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
