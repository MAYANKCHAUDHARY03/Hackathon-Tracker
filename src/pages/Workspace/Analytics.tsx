import { useEffect, useState } from 'react';
import { 
  BarChart, Activity, Users, FolderKanban, 
  Trophy, CheckCircle2, CircleDashed 
} from 'lucide-react';
import { analyticsApi } from '@/api/analyticsApi';
import type { WorkspaceAnalyticsSummary } from '@/api/analyticsApi';
import { useWorkspaceStore } from '@/store/workspaceStore';


export default function Analytics() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [data, setData] = useState<WorkspaceAnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspaceId) return;

    const fetchAnalytics = async () => {
      try {
        const response = await analyticsApi.getWorkspaceAnalytics(activeWorkspaceId);
        setData(response);
      } catch (error) {
        console.error('Failed to load analytics', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [activeWorkspaceId]);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground mt-2">Loading workspace analytics...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-32 bg-card border border-border rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Hackathons', value: data.total_hackathons, icon: Trophy, color: 'text-yellow-500' },
    { label: 'Active Hackathons', value: data.active_hackathons, icon: Activity, color: 'text-green-500' },
    { label: 'Total Projects', value: data.total_projects, icon: FolderKanban, color: 'text-blue-500' },
    { label: 'Total Teams', value: data.total_teams, icon: Users, color: 'text-indigo-500' },
    { label: 'Total Members', value: data.total_users, icon: Users, color: 'text-purple-500' },
    { label: 'Tasks Completed', value: data.tasks_completed, icon: CheckCircle2, color: 'text-emerald-500' },
    { label: 'Tasks Pending', value: data.tasks_pending, icon: CircleDashed, color: 'text-orange-500' },
    { label: 'Recent Activities', value: data.recent_activity_count, icon: BarChart, color: 'text-pink-500' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics Overview</h1>
        <p className="text-muted-foreground mt-2">High-level metrics and statistics for this workspace.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <div key={index} className="glass-panel p-6 flex flex-col justify-between hover-lift">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">{stat.label}</p>
                <h3 className="text-3xl font-bold text-foreground">{stat.value}</h3>
              </div>
              <div className={`p-3 rounded-xl bg-card border border-border/50 shadow-sm ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Visualizations can be added here in the future */}
    </div>
  );
}
