import { useEffect, useState } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { auditApi, type AuditLog } from '@/api/auditApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { format } from 'date-fns';
import { Download } from 'lucide-react';
import { toast } from 'sonner';

export function AuditLogs() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspaceId) return;
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const response = await auditApi.getAuditLogs(activeWorkspaceId, 0, 100);
        setLogs(response.items);
      } catch (error) {
        console.error(error);
        toast.error('Failed to fetch audit logs');
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [activeWorkspaceId]);

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audit Logs</h2>
          <p className="text-muted-foreground mt-1">Immutable record of all critical actions performed in the workspace.</p>
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export CSV
        </Button>
      </div>

      <GlassPanel className="p-6">
        <div className="rounded-md border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Resource Type</TableHead>
                <TableHead>Resource ID</TableHead>
                <TableHead>Actor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center h-24">Loading...</TableCell>
                </TableRow>
              ) : logs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">No audit logs found.</TableCell>
                </TableRow>
              ) : (
                logs.map(log => (
                  <TableRow key={log.id}>
                    <TableCell className="text-sm font-medium">
                      {format(new Date(log.created_at), 'yyyy-MM-dd HH:mm:ss')}
                    </TableCell>
                    <TableCell>
                      <span className="px-2 py-1 rounded bg-secondary text-secondary-foreground text-xs font-semibold uppercase tracking-wider">
                        {log.action}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{log.resource_type}</TableCell>
                    <TableCell className="text-sm truncate max-w-[150px]">{log.resource_id}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{log.actor_id || 'System'}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </GlassPanel>
    </div>
  );
}
