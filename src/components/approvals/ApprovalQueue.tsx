import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentApprovalApi, type AgentApprovalRequest } from '@/api/agentApprovalApi';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, CheckCircle2, XCircle, Bot } from 'lucide-react';
import { toast } from 'sonner';
import { format } from 'date-fns';

export function ApprovalQueue() {
  const queryClient = useQueryClient();

  const { data: pendingApprovals, isLoading } = useQuery({
    queryKey: ['agent-approvals'],
    queryFn: agentApprovalApi.getPendingApprovals,
    refetchInterval: 10000, // Poll every 10 seconds
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => agentApprovalApi.approveRequest(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['agent-approvals'] });
      if (data.status === 'success') {
        toast.success('Agent request approved and executed.');
      } else {
        toast.error(`Agent tool execution failed: ${data.error}`);
      }
    },
    onError: () => toast.error('Failed to approve request.'),
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) => agentApprovalApi.rejectRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-approvals'] });
      toast.success('Agent request rejected.');
    },
    onError: () => toast.error('Failed to reject request.'),
  });

  if (isLoading) {
    return <div>Loading pending approvals...</div>;
  }

  const requests = pendingApprovals || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-orange-500" />
          Agent Approval Queue
        </CardTitle>
        <CardDescription>
          Review and approve high-risk actions requested by AI agents across the platform.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {requests.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed rounded-lg bg-muted/20 flex flex-col items-center">
            <ShieldAlert className="w-8 h-8 text-muted-foreground mb-3" />
            <h3 className="text-lg font-medium">No Pending Approvals</h3>
            <p className="text-sm text-muted-foreground mt-1">All agent operations are currently functioning within autonomous limits.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((req) => (
              <div key={req.id} className="border rounded-lg p-4 bg-card">
                <div className="flex flex-col md:flex-row justify-between md:items-start gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4 text-primary" />
                      <span className="font-semibold text-lg">{req.agent_name}</span>
                      <Badge variant="outline" className="uppercase text-orange-600 border-orange-200 bg-orange-50">
                        {req.risk_level} Risk
                      </Badge>
                    </div>
                    <div className="text-sm">
                      <span className="text-muted-foreground">Requested Tool: </span>
                      <span className="font-mono bg-muted px-1 py-0.5 rounded text-xs">{req.tool_name}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Justification</p>
                      <p className="text-sm text-muted-foreground mt-1">{req.justification || 'No justification provided.'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Parameters</p>
                      <pre className="text-xs bg-muted p-2 rounded-md mt-1 overflow-x-auto">
                        {JSON.stringify(req.parameters_json, null, 2)}
                      </pre>
                    </div>
                    <div className="text-xs text-muted-foreground pt-2">
                      Requested on: {format(new Date(req.requested_at), 'PPP pp')}
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-2 shrink-0 md:pt-1">
                    <Button 
                      onClick={() => approveMutation.mutate(req.id)} 
                      disabled={approveMutation.isPending || rejectMutation.isPending}
                      size="sm"
                      className="bg-green-600 hover:bg-green-700 text-white w-full sm:w-auto"
                    >
                      <CheckCircle2 className="w-4 h-4 mr-1" /> Approve & Execute
                    </Button>
                    <Button 
                      onClick={() => rejectMutation.mutate(req.id)} 
                      disabled={approveMutation.isPending || rejectMutation.isPending}
                      variant="destructive"
                      size="sm"
                      className="w-full sm:w-auto"
                    >
                      <XCircle className="w-4 h-4 mr-1" /> Reject
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
