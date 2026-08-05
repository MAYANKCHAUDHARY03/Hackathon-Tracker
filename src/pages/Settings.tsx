import { useEffect, useState } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import { Mail, Send, Trash2, Users } from 'lucide-react';
import { format } from 'date-fns';

interface Invitation {
  id: string;
  email: string;
  status: string;
  workspace_role: string;
  created_at: string;
  expires_at: string;
  token_hash: string;
}

export default function Settings() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('member');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    if (activeWorkspaceId) {
      loadInvitations();
    }
  }, [activeWorkspaceId]);

  async function loadInvitations() {
    try {
      const data = await apiClient.get<Invitation[]>(`/workspaces/${activeWorkspaceId}/invitations`);
      setInvitations(data);
    } catch (err) {
      console.error('Failed to load invitations', err);
    }
  }

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;
    setIsLoading(true);
    setMessage(null);
    try {
      await apiClient.post(`/workspaces/${activeWorkspaceId}/invitations`, { email, role });
      setMessage({ type: 'success', text: 'Invitation sent!' });
      setEmail('');
      loadInvitations();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.data?.detail || 'Failed to send invitation' });
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRevoke(id: string) {
    try {
      await apiClient.delete(`/invitations/${id}`);
      loadInvitations();
    } catch (err: any) {
      alert(err.data?.detail || 'Failed to revoke invitation');
    }
  }

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Workspace Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your workspace members and invitations.</p>
      </div>

      <GlassPanel className="p-6 space-y-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Users className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight">Invite Members</h2>
        </div>

        <form onSubmit={handleInvite} className="flex gap-4 items-end">
          <div className="flex-1 space-y-2">
            <label className="text-sm font-medium">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="colleague@example.com"
                className="w-full h-10 pl-9 pr-4 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
            </div>
          </div>
          
          <div className="w-48 space-y-2">
            <label className="text-sm font-medium">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-secondary/30 border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <Button type="submit" disabled={isLoading} className="gap-2 h-10">
            <Send className="h-4 w-4" />
            {isLoading ? 'Sending...' : 'Send Invite'}
          </Button>
        </form>

        {message && (
          <div className={`p-3 rounded-md text-sm ${message.type === 'error' ? 'bg-destructive/10 text-destructive' : 'bg-green-500/10 text-green-500'}`}>
            {message.text}
          </div>
        )}

        <div className="pt-6 border-t border-border/50">
          <h3 className="text-sm font-medium text-muted-foreground mb-4">Pending Invitations</h3>
          
          {invitations.length === 0 ? (
            <p className="text-sm text-muted-foreground italic">No pending invitations.</p>
          ) : (
            <div className="space-y-3">
              {invitations.map(inv => (
                <div key={inv.id} className="flex items-center justify-between p-3 rounded-lg bg-secondary/20 border border-border/30">
                  <div>
                    <p className="font-medium text-sm">{inv.email}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 flex gap-2">
                      <span className="capitalize">{inv.workspace_role}</span>
                      <span>•</span>
                      <span>Expires {format(new Date(inv.expires_at), 'MMM d, yyyy')}</span>
                    </p>
                    <p className="text-xs text-primary mt-1 font-mono break-all">
                      {window.location.origin}/invitations/{inv.token_hash}/accept
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => handleRevoke(inv.id)} className="text-destructive hover:text-destructive hover:bg-destructive/10" title="Revoke Invitation">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </GlassPanel>
    </div>
  );
}
