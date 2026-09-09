import { useEffect, useState, useRef } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import { exportImportApi } from '@/api/exportImportApi';
import { Mail, Send, Trash2, Users, Bell, Download, Upload } from 'lucide-react';
import { format } from 'date-fns';
import { NotificationSettings } from '@/components/notifications/NotificationSettings';
import { IntegrationSettings } from '@/components/settings/IntegrationSettings';
import { AutomationSettings } from '@/components/settings/AutomationSettings';
import { LinkIcon, Zap } from 'lucide-react';

import { InvitationManager } from '@/components/workspace/InvitationManager';

export default function Settings() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleExport() {
    if (!activeWorkspaceId) return;
    setExporting(true);
    try {
      const res = await exportImportApi.exportWorkspace(activeWorkspaceId);
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(res, null, 2));
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", `workspace_export_${activeWorkspaceId}.json`);
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    } catch (err) {
      console.error(err);
      alert('Export failed');
    } finally {
      setExporting(false);
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !activeWorkspaceId) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        setImporting(true);
        const previewRes = await exportImportApi.previewImport(activeWorkspaceId, json);
        if (!previewRes.is_valid) {
          alert('Import Invalid: ' + previewRes.errors.join(', '));
          return;
        }
        
        if (confirm(`Valid backup found with ${previewRes.hackathons_count} hackathons, ${previewRes.projects_count} projects, and ${previewRes.teams_count} teams. Proceed with import? (Data will be added)`)) {
          await exportImportApi.executeImport(activeWorkspaceId, json, false);
          alert('Import successful');
        }
      } catch (err) {
        console.error(err);
        alert('Invalid JSON file or import failed');
      } finally {
        setImporting(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    };
    reader.readAsText(file);
  };

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Workspace Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your workspace members and invitations.</p>
      </div>

      <InvitationManager />

      <GlassPanel className="p-6 space-y-6 mt-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Bell className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">Notification Preferences</h2>
        </div>
        <NotificationSettings />
      </GlassPanel>

      <GlassPanel className="p-6 space-y-6 mt-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Download className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">Data Management</h2>
        </div>
        
        <div className="flex flex-col gap-4 max-w-md">
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg border border-border/50">
            <div>
              <p className="font-medium">Export Workspace Data</p>
              <p className="text-sm text-muted-foreground">Download a complete JSON backup.</p>
            </div>
            <Button onClick={handleExport} disabled={exporting} variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              {exporting ? 'Exporting...' : 'Export'}
            </Button>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg border border-border/50">
            <div>
              <p className="font-medium">Import Workspace Data</p>
              <p className="text-sm text-muted-foreground">Restore data from a previous backup.</p>
            </div>
            <input type="file" accept=".json" className="hidden" ref={fileInputRef} onChange={handleFileUpload} />
            <Button onClick={() => fileInputRef.current?.click()} disabled={importing} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              {importing ? 'Importing...' : 'Import'}
            </Button>
          </div>
        </div>
      </GlassPanel>

      <GlassPanel className="p-6 space-y-6 mt-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Zap className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">Automation Rules</h2>
        </div>
        <AutomationSettings />
      </GlassPanel>

      <GlassPanel className="p-6 space-y-6 mt-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-primary/20 rounded-lg">
            <LinkIcon className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">External Integrations</h2>
        </div>
        <IntegrationSettings />
      </GlassPanel>
    </div>
  );
}
