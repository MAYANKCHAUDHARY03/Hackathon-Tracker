import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Button } from '@/components/ui/button';
import { GlassPanel } from '@/components/ui/glass-panel';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export default function AcceptInvitation() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { setActiveWorkspace } = useWorkspaceStore();
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Verifying invitation...');
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);

  useEffect(() => {
    async function acceptInvite() {
      if (!token) {
        setStatus('error');
        setMessage('Invalid invitation link.');
        return;
      }
      try {
        const response = await apiClient.post<{ status: string; workspace_id: string }>(
          `/invitations/${token}/accept`,
          {}
        );
        setStatus('success');
        setMessage('Invitation accepted successfully!');
        setWorkspaceId(response.workspace_id);
      } catch (err: any) {
        setStatus('error');
        setMessage(err.data?.detail || 'Failed to accept invitation. It may have expired.');
      }
    }
    acceptInvite();
  }, [token]);

  const handleContinue = () => {
    if (workspaceId) {
      setActiveWorkspace(workspaceId);
    }
    navigate('/');
  };

  return (
    <div className="flex h-screen items-center justify-center p-4">
      <GlassPanel className="w-full max-w-md p-8 text-center space-y-6">
        {status === 'loading' && (
          <div className="flex flex-col items-center">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <h2 className="text-xl font-semibold">Accepting Invitation...</h2>
            <p className="text-muted-foreground mt-2">{message}</p>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mb-4" />
            <h2 className="text-xl font-semibold">Success!</h2>
            <p className="text-muted-foreground mt-2">{message}</p>
            <Button onClick={handleContinue} className="mt-6 w-full">
              Go to Dashboard
            </Button>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center">
            <XCircle className="h-16 w-16 text-destructive mb-4" />
            <h2 className="text-xl font-semibold">Error</h2>
            <p className="text-muted-foreground mt-2">{message}</p>
            <Button onClick={() => navigate('/')} variant="outline" className="mt-6 w-full">
              Return to Home
            </Button>
          </div>
        )}
      </GlassPanel>
    </div>
  );
}
