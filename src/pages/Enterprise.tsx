import { useEffect, useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Shield, Key, Activity, ShieldCheck, Server, RefreshCw } from 'lucide-react';
import { enterpriseApi, type HealthResponse, type MetricsResponse } from '@/api/enterprise';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { IntegrationHub } from '@/components/integrations/IntegrationHub';
import { AuditLogs } from '@/components/enterprise/AuditLogs';
import { WebhookSettings } from '@/components/enterprise/WebhookSettings';

export default function Enterprise() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [scimToken, setScimToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function fetchOpsData() {
    setLoading(true);
    try {
      const h = await enterpriseApi.getHealth();
      setHealth(h);
      const m = await enterpriseApi.getMetrics();
      setMetrics(m);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOpsData();
    const interval = setInterval(fetchOpsData, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const generateToken = () => {
    // Mock token generation for UI demonstration since backend endpoint is pending
    const randomHex = [...Array(64)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
    setScimToken(`scim_v2_${randomHex}`);
  };

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Enterprise Settings</h1>
        <p className="text-muted-foreground mt-1">Manage Identity Providers, SCIM, and Monitor Production Health.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* System Health */}
        <GlassPanel className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-primary/20 rounded-lg">
                <Activity className="h-5 w-5 text-primary" />
              </div>
              <h2 className="text-xl font-semibold tracking-tight">System Health</h2>
            </div>
            <Button variant="ghost" size="sm" onClick={fetchOpsData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
          
          <div className="space-y-3 pt-2">
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/30 border border-border/50">
              <span className="font-medium text-sm">Overall Status</span>
              <span className={`text-sm font-bold ${health?.status === 'ok' ? 'text-green-500' : 'text-yellow-500'}`}>
                {health?.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/30 border border-border/50">
              <span className="font-medium text-sm">Database</span>
              <span className={`text-sm font-bold ${health?.services?.database === 'ok' ? 'text-green-500' : 'text-red-500'}`}>
                {health?.services?.database?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/30 border border-border/50">
              <span className="font-medium text-sm">API Gateway</span>
              <span className={`text-sm font-bold ${health?.services?.api === 'ok' ? 'text-green-500' : 'text-red-500'}`}>
                {health?.services?.api?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
          </div>
        </GlassPanel>

        {/* System Metrics */}
        <GlassPanel className="p-6 space-y-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/20 rounded-lg">
              <Server className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold tracking-tight">Node Metrics</h2>
          </div>
          
          <div className="space-y-3 pt-2">
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>CPU Usage</span>
                <span className="font-mono">{metrics?.system_cpu_usage_percent?.toFixed(1) || '0.0'}%</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-500"
                  style={{ width: `${metrics?.system_cpu_usage_percent || 0}%` }}
                />
              </div>
            </div>

            <div className="space-y-1 pt-2">
              <div className="flex justify-between text-sm">
                <span>Memory Usage</span>
                <span className="font-mono">{metrics?.system_memory_usage_percent?.toFixed(1) || '0.0'}%</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-500"
                  style={{ width: `${metrics?.system_memory_usage_percent || 0}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground text-right mt-1">
                {metrics ? (metrics.system_memory_available_bytes / 1024 / 1024 / 1024).toFixed(2) : '0'} GB Available
              </p>
            </div>
          </div>
        </GlassPanel>

        {/* SCIM Provisioning */}
        <GlassPanel className="p-6 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-2 bg-primary/20 rounded-lg">
              <Key className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold tracking-tight">SCIM Provisioning</h2>
          </div>
          
          <p className="text-sm text-muted-foreground">
            Generate a bearer token to securely provision users from Azure AD, Okta, or other IdPs via the SCIM 2.0 API.
          </p>
          
          <div className="pt-2">
            {scimToken ? (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-destructive">Copy this token now. It will not be shown again.</p>
                <div className="p-3 bg-black/50 border border-primary/30 rounded-md font-mono text-xs break-all text-primary">
                  {scimToken}
                </div>
              </div>
            ) : (
              <Button onClick={generateToken} className="w-full">
                Generate SCIM Token
              </Button>
            )}
          </div>
        </GlassPanel>

        {/* Identity Providers */}
        <GlassPanel className="p-6 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-2 bg-primary/20 rounded-lg">
              <ShieldCheck className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold tracking-tight">Identity Providers</h2>
          </div>
          
          <p className="text-sm text-muted-foreground">
            Configure OIDC and SAML 2.0 identity providers to allow organization members to authenticate securely.
          </p>

          <div className="space-y-3 pt-2">
            <div className="p-3 border border-border/50 rounded-lg bg-secondary/20 flex justify-between items-center opacity-70">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-blue-400" />
                <div>
                  <p className="font-medium text-sm">Azure Active Directory</p>
                  <p className="text-xs text-muted-foreground">OIDC / Pending Configuration</p>
                </div>
              </div>
              <Button variant="outline" size="sm" disabled>Configure</Button>
            </div>

            <div className="p-3 border border-border/50 rounded-lg bg-secondary/20 flex justify-between items-center opacity-70">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-purple-400" />
                <div>
                  <p className="font-medium text-sm">Okta SAML</p>
                  <p className="text-xs text-muted-foreground">SAML 2.0 / Not Connected</p>
                </div>
              </div>
              <Button variant="outline" size="sm" disabled>Configure</Button>
            </div>
          </div>
        </GlassPanel>

        {/* Integration Hub */}
        <div className="md:col-span-2">
          <IntegrationHub />
        </div>

        {/* Audit Logs */}
        <div className="md:col-span-2">
          <AuditLogs />
        </div>

        {/* Webhooks */}
        <div className="md:col-span-2">
          <WebhookSettings />
        </div>
      </div>
    </div>
  );
}
