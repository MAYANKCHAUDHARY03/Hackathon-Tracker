import React, { useState, useEffect } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Activity, AlertTriangle, CheckCircle2, ShieldAlert, Zap, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Alert {
  id: string;
  severity: string;
  message: string;
  source: string;
  timestamp: string;
}

interface ActiveProgramStat {
  program_id: string;
  name: string;
  active_teams: number;
  pending_evaluations: number;
  at_risk_projects: number;
}

interface OperationsCenterStatus {
  total_active_programs: number;
  total_active_users: number;
  total_pending_evaluations: number;
  critical_incidents: number;
  active_programs: ActiveProgramStat[];
  live_alerts: Alert[];
}

export default function OperationsCenter() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [data, setData] = useState<OperationsCenterStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!activeWorkspaceId) return;
      setLoading(true);
      try {
        const response = await apiClient.get<OperationsCenterStatus>(`/workspaces/${activeWorkspaceId}/operations-center`);
        setData(response);
      } catch (err) {
        console.error('Failed to load operations center data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    
    // Poll every 30s to simulate "real-time"
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [activeWorkspaceId]);

  if (loading && !data) {
    return <div className="p-8 text-center animate-pulse">Loading Operations Center...</div>;
  }

  if (!data) return <div className="p-8 text-center text-red-500">Failed to load operations data.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-border/50 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" /> Operations Center
          </h1>
          <p className="text-muted-foreground mt-1">Real-time program-wide visibility and autonomous alerts.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm font-medium border border-green-500/20">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          Live Connection
        </div>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlassPanel className="p-4 flex flex-col justify-center items-center text-center">
          <span className="text-3xl font-bold">{data.total_active_programs}</span>
          <span className="text-sm text-muted-foreground">Active Programs</span>
        </GlassPanel>
        <GlassPanel className="p-4 flex flex-col justify-center items-center text-center">
          <span className="text-3xl font-bold">{data.total_active_users}</span>
          <span className="text-sm text-muted-foreground">Active Users</span>
        </GlassPanel>
        <GlassPanel className="p-4 flex flex-col justify-center items-center text-center">
          <span className="text-3xl font-bold">{data.total_pending_evaluations}</span>
          <span className="text-sm text-muted-foreground">Pending Evaluations</span>
        </GlassPanel>
        <GlassPanel className={`p-4 flex flex-col justify-center items-center text-center ${data.critical_incidents > 0 ? 'bg-red-500/10 border-red-500/20' : ''}`}>
          <span className={`text-3xl font-bold ${data.critical_incidents > 0 ? 'text-red-500' : 'text-green-500'}`}>
            {data.critical_incidents}
          </span>
          <span className={`text-sm ${data.critical_incidents > 0 ? 'text-red-500/80' : 'text-green-500/80'}`}>Critical Incidents</span>
        </GlassPanel>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Programs Overview */}
        <GlassPanel className="p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Active Programs Pulse</h2>
          <div className="space-y-4">
            {data.active_programs.map((prog) => (
              <div key={prog.program_id} className="p-4 bg-secondary/20 rounded-lg border border-border/50 flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-foreground">{prog.name}</h3>
                  <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1"><Users className="h-3 w-3"/> {prog.active_teams} Teams</span>
                    <span className="flex items-center gap-1"><CheckCircle2 className="h-3 w-3"/> {prog.pending_evaluations} Evals Pending</span>
                  </div>
                </div>
                {prog.at_risk_projects > 0 ? (
                  <div className="px-3 py-1 bg-amber-500/10 text-amber-500 rounded border border-amber-500/20 text-sm font-medium flex items-center gap-1">
                    <AlertTriangle className="h-4 w-4" /> {prog.at_risk_projects} At Risk
                  </div>
                ) : (
                  <div className="px-3 py-1 bg-green-500/10 text-green-500 rounded border border-green-500/20 text-sm font-medium">
                    Healthy
                  </div>
                )}
              </div>
            ))}
            {data.active_programs.length === 0 && (
              <p className="text-muted-foreground text-sm">No active programs right now.</p>
            )}
          </div>
        </GlassPanel>

        {/* Live Copilot Alerts */}
        <GlassPanel className="p-6 flex flex-col h-[500px]">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="h-5 w-5 text-yellow-500" />
            <h2 className="text-lg font-semibold">Live AI Alerts</h2>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 space-y-3">
            {data.live_alerts.map((alert) => (
              <div key={alert.id} className={`p-3 rounded-lg border-l-4 bg-secondary/10 ${
                alert.severity === 'CRITICAL' ? 'border-l-red-500' :
                alert.severity === 'WARNING' ? 'border-l-amber-500' : 'border-l-blue-500'
              }`}>
                <div className="flex justify-between items-start mb-1">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{alert.source}</span>
                  <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}
                  </span>
                </div>
                <p className={`text-sm ${alert.severity === 'CRITICAL' ? 'font-medium text-foreground' : 'text-muted-foreground'}`}>
                  {alert.message}
                </p>
              </div>
            ))}
            {data.live_alerts.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
                <ShieldAlert className="h-8 w-8 mb-2 opacity-50" />
                <p className="text-sm">No alerts at the moment.</p>
              </div>
            )}
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
