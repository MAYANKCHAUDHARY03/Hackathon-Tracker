import { useEffect, useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { analyticsApi } from '@/api/analyticsApi';
import type { AnalyticsOverview, AnalyticsDemographics, AnalyticsEvaluations } from '@/api/analyticsApi';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, Briefcase, FileText, Activity } from 'lucide-react';
import { toast } from 'sonner';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7'];

export function AnalyticsDashboard() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [demographics, setDemographics] = useState<AnalyticsDemographics | null>(null);
  const [evaluations, setEvaluations] = useState<AnalyticsEvaluations | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspaceId) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [o, d, e] = await Promise.all([
          analyticsApi.getOverview(activeWorkspaceId),
          analyticsApi.getDemographics(activeWorkspaceId),
          analyticsApi.getEvaluations(activeWorkspaceId)
        ]);
        setOverview(o.data);
        setDemographics(d.data);
        setEvaluations(e.data);
      } catch (err) {
        console.error(err);
        toast.error('Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [activeWorkspaceId]);

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  if (loading) {
    return <div className="p-8">Loading analytics...</div>;
  }

  const roleData = demographics ? Object.entries(demographics.roles_distribution).map(([name, value]) => ({ name, value })) : [];
  const skillData = demographics ? Object.entries(demographics.skills_distribution).map(([name, value]) => ({ name, value })) : [];
  
  const scoreData = evaluations ? [
    { name: '0-20', count: evaluations.score_distribution.range_0_20 },
    { name: '21-40', count: evaluations.score_distribution.range_21_40 },
    { name: '41-60', count: evaluations.score_distribution.range_41_60 },
    { name: '61-80', count: evaluations.score_distribution.range_61_80 },
    { name: '81-100', count: evaluations.score_distribution.range_81_100 },
  ] : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Analytics Overview</h2>
        <p className="text-muted-foreground mt-1">Key metrics and insights for your innovation ecosystem.</p>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassPanel className="p-6 flex items-center gap-4">
          <div className="p-3 bg-primary/20 rounded-lg">
            <Users className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Users</p>
            <h3 className="text-2xl font-bold">{overview?.total_users || 0}</h3>
          </div>
        </GlassPanel>
        
        <GlassPanel className="p-6 flex items-center gap-4">
          <div className="p-3 bg-primary/20 rounded-lg">
            <Briefcase className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Teams</p>
            <h3 className="text-2xl font-bold">{overview?.total_teams || 0}</h3>
          </div>
        </GlassPanel>

        <GlassPanel className="p-6 flex items-center gap-4">
          <div className="p-3 bg-primary/20 rounded-lg">
            <Activity className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Projects</p>
            <h3 className="text-2xl font-bold">{overview?.total_projects || 0}</h3>
          </div>
        </GlassPanel>

        <GlassPanel className="p-6 flex items-center gap-4">
          <div className="p-3 bg-primary/20 rounded-lg">
            <FileText className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Avg Score</p>
            <h3 className="text-2xl font-bold">{evaluations?.average_score || 0}</h3>
          </div>
        </GlassPanel>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Roles Distribution */}
        <GlassPanel className="p-6 space-y-4">
          <h3 className="text-lg font-semibold tracking-tight">Participant Roles</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={roleData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {roleData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-2 justify-center">
            {roleData.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-1 text-xs text-muted-foreground">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                {entry.name} ({entry.value})
              </div>
            ))}
          </div>
        </GlassPanel>

        {/* Score Distribution */}
        <GlassPanel className="p-6 space-y-4">
          <h3 className="text-lg font-semibold tracking-tight">Score Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreData}>
                <XAxis dataKey="name" fontSize={12} stroke="#888" />
                <YAxis fontSize={12} stroke="#888" />
                <Tooltip cursor={{ fill: 'rgba(255, 255, 255, 0.1)' }} />
                <Bar dataKey="count" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
