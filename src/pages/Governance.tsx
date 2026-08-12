import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { governanceApi, type WorkspacePolicy, type DSR, type AuditLog } from '@/api/governanceApi';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  ShieldCheck, 
  Database, 
  Clock, 
  BrainCircuit,
  Save,
  UserX,
  FileDown,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';
import { format } from 'date-fns';

export default function Governance() {
  const { currentWorkspace } = useWorkspaceStore();
  const workspaceId = currentWorkspace?.id;
  const queryClient = useQueryClient();

  const { data: policy, isLoading: isLoadingPolicy } = useQuery({
    queryKey: ['workspace-policy', workspaceId],
    queryFn: () => governanceApi.getPolicy(workspaceId!),
    enabled: !!workspaceId,
  });

  const { data: dsrs, isLoading: isLoadingDSRs } = useQuery({
    queryKey: ['governance-dsrs', workspaceId],
    queryFn: () => governanceApi.getDSRs(workspaceId!),
    enabled: !!workspaceId,
  });

  const { data: auditLogs, isLoading: isLoadingAudit } = useQuery({
    queryKey: ['governance-audit', workspaceId],
    queryFn: () => governanceApi.getAuditLogs(workspaceId!),
    enabled: !!workspaceId,
  });

  const updatePolicyMutation = useMutation({
    mutationFn: (data: WorkspacePolicy) => governanceApi.updatePolicy(workspaceId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-policy', workspaceId] });
      queryClient.invalidateQueries({ queryKey: ['governance-audit', workspaceId] });
      toast.success('Governance policy updated successfully.');
    },
    onError: () => toast.error('Failed to update policy.'),
  });

  const updateDSRStatusMutation = useMutation({
    mutationFn: ({ dsrId, status, notes }: { dsrId: string; status: string; notes: string }) => 
      governanceApi.updateDSRStatus(workspaceId!, dsrId, status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance-dsrs', workspaceId] });
      toast.success('DSR status updated.');
    },
    onError: () => toast.error('Failed to update DSR status.'),
  });

  if (!workspaceId) {
    return <div>Select a workspace to view governance settings.</div>;
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Governance & Compliance</h1>
          <p className="text-muted-foreground mt-1">
            Manage data residency, retention policies, privacy requests, and audit logs.
          </p>
        </div>
      </div>

      <Tabs defaultValue="policy" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="policy">Workspace Policy</TabsTrigger>
          <TabsTrigger value="dsr">Data Subject Requests</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="policy" className="mt-6 space-y-6">
          <PolicyTab 
            policy={policy} 
            isLoading={isLoadingPolicy} 
            onSave={(data) => updatePolicyMutation.mutate(data)} 
            isSaving={updatePolicyMutation.isPending}
          />
        </TabsContent>

        <TabsContent value="dsr" className="mt-6">
          <DSRTab 
            dsrs={dsrs || []} 
            isLoading={isLoadingDSRs} 
            onUpdateStatus={(dsrId, status, notes) => updateDSRStatusMutation.mutate({ dsrId, status, notes })}
          />
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <AuditLogTab logs={auditLogs || []} isLoading={isLoadingAudit} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function PolicyTab({ policy, isLoading, onSave, isSaving }: { policy?: WorkspacePolicy; isLoading: boolean; onSave: (d: WorkspacePolicy) => void; isSaving: boolean }) {
  const [formData, setFormData] = React.useState<WorkspacePolicy>({
    data_residency: 'US',
    retention_days: 365,
    ai_consent: false,
  });

  React.useEffect(() => {
    if (policy) {
      setFormData(policy);
    }
  }, [policy]);

  if (isLoading) return <div>Loading policies...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-primary" />
          Data & Security Policies
        </CardTitle>
        <CardDescription>
          Configure how data is stored, retained, and utilized across your workspace.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Data Residency Region</Label>
          <Select 
            value={formData.data_residency} 
            onValueChange={(val) => setFormData(f => ({ ...f, data_residency: val }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="US">United States (US)</SelectItem>
              <SelectItem value="EU">European Union (EU)</SelectItem>
              <SelectItem value="UK">United Kingdom (UK)</SelectItem>
              <SelectItem value="GLOBAL">Global (Multi-region)</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
            <Database className="h-4 w-4" /> Determines the primary storage region for workspace data.
          </p>
        </div>

        <div className="space-y-2">
          <Label>Data Retention (Days)</Label>
          <Input 
            type="number" 
            min={30} 
            max={3650} 
            value={formData.retention_days} 
            onChange={(e) => setFormData(f => ({ ...f, retention_days: parseInt(e.target.value) || 365 }))} 
          />
          <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
            <Clock className="h-4 w-4" /> Hard-delete data after this period.
          </p>
        </div>

        <div className="flex items-center justify-between rounded-lg border p-4">
          <div className="space-y-0.5">
            <Label className="text-base flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-blue-500" />
              Organization AI Consent
            </Label>
            <p className="text-sm text-muted-foreground">
              Allow non-PII workspace data to be used for fine-tuning platform AI models.
            </p>
          </div>
          <Switch 
            checked={formData.ai_consent} 
            onCheckedChange={(val) => setFormData(f => ({ ...f, ai_consent: val }))} 
          />
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={() => onSave(formData)} disabled={isSaving}>
          {isSaving ? 'Saving...' : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Policies
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}

function DSRTab({ dsrs, isLoading, onUpdateStatus }: { dsrs: DSR[]; isLoading: boolean; onUpdateStatus: (id: string, status: string, notes: string) => void }) {
  if (isLoading) return <div>Loading requests...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Data Subject Requests (DSRs)</CardTitle>
        <CardDescription>
          Manage GDPR/CCPA privacy requests from workspace users.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {dsrs.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No active data subject requests.
          </div>
        ) : (
          <div className="space-y-4">
            {dsrs.map(dsr => (
              <div key={dsr.id} className="border rounded-lg p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">Request: {dsr.id.substring(0, 8)}...</span>
                    <Badge variant={dsr.status === 'completed' ? 'default' : dsr.status === 'pending' ? 'secondary' : 'outline'}>
                      {dsr.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
                    {dsr.request_type === 'export' ? <FileDown className="h-4 w-4" /> : <UserX className="h-4 w-4" />}
                    Type: <span className="uppercase">{dsr.request_type}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Submitted: {format(new Date(dsr.created_at), 'PPP')}</p>
                </div>

                <div className="flex gap-2">
                  {dsr.status !== 'completed' && dsr.status !== 'rejected' && (
                    <>
                      <Button variant="outline" size="sm" onClick={() => onUpdateStatus(dsr.id, 'completed', 'Processed manually.')}>
                        Mark Completed
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => onUpdateStatus(dsr.id, 'rejected', 'Invalid request.')}>
                        Reject
                      </Button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function AuditLogTab({ logs, isLoading }: { logs: AuditLog[]; isLoading: boolean }) {
  if (isLoading) return <div>Loading audit logs...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Security Audit Logs
        </CardTitle>
        <CardDescription>
          Immutable ledger of critical governance and security events.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {logs.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No audit logs found for this workspace.
          </div>
        ) : (
          <div className="rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50 text-left">
                  <th className="p-3 font-medium">Timestamp</th>
                  <th className="p-3 font-medium">Action</th>
                  <th className="p-3 font-medium">Resource</th>
                  <th className="p-3 font-medium">Actor</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b last:border-0 hover:bg-muted/30">
                    <td className="p-3 whitespace-nowrap">{format(new Date(log.created_at), 'Pp')}</td>
                    <td className="p-3 font-medium text-primary">{log.action}</td>
                    <td className="p-3">{log.target_resource || 'N/A'}</td>
                    <td className="p-3 font-mono text-xs">{log.actor_id ? log.actor_id.substring(0, 8) + '...' : 'System'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
