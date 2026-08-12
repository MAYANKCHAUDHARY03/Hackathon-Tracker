import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { useWorkspaceStore } from '@/store/workspaceStore'
import { federationApi } from '@/api/federationApi'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

export default function Federation() {
  const currentWorkspace = useWorkspaceStore((state) => state.activeWorkspaceId)
  const queryClient = useQueryClient()
  const [newTargetId, setNewTargetId] = useState('')

  const { data: links, isLoading } = useQuery({
    queryKey: ['federation', currentWorkspace],
    queryFn: () => federationApi.getLinks(currentWorkspace!),
    enabled: !!currentWorkspace,
  })

  const createMutation = useMutation({
    mutationFn: (targetId: string) => federationApi.createLink(currentWorkspace!, { target_workspace_id: targetId, shared_entities: [] }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['federation', currentWorkspace] })
      setNewTargetId('')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ linkId, status }: { linkId: string, status: string }) => 
      federationApi.updateLinkStatus(currentWorkspace!, linkId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['federation', currentWorkspace] })
    },
  })

  if (!currentWorkspace) {
    return <div className="p-8">Please select a workspace first.</div>
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ecosystem Federation</h1>
          <p className="text-muted-foreground mt-2">
            Connect your workspace with other ecosystems to share resources, talent, and opportunities.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Create Federation Link</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <input 
              type="text"
              placeholder="Target Workspace ID"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={newTargetId}
              onChange={(e) => setNewTargetId(e.target.value)}
            />
            <Button 
              onClick={() => createMutation.mutate(newTargetId)}
              disabled={!newTargetId || createMutation.isPending}
            >
              Request Federation
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Inbound Connections</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div>Loading...</div>
            ) : (
              <div className="space-y-4">
                {links?.filter(l => l.target_workspace_id === currentWorkspace).map(link => (
                  <div key={link.id} className="flex justify-between items-center p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">From: {link.source_workspace_id}</p>
                      <p className="text-sm text-muted-foreground">Status: {link.status}</p>
                    </div>
                    {link.status === 'PENDING' && (
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => updateMutation.mutate({ linkId: link.id, status: 'ACCEPTED' })}>Accept</Button>
                        <Button size="sm" variant="outline" onClick={() => updateMutation.mutate({ linkId: link.id, status: 'REJECTED' })}>Reject</Button>
                      </div>
                    )}
                  </div>
                ))}
                {links?.filter(l => l.target_workspace_id === currentWorkspace).length === 0 && (
                  <p className="text-muted-foreground">No inbound connections.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Outbound Connections</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div>Loading...</div>
            ) : (
              <div className="space-y-4">
                {links?.filter(l => l.source_workspace_id === currentWorkspace).map(link => (
                  <div key={link.id} className="flex justify-between items-center p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">To: {link.target_workspace_id}</p>
                      <p className="text-sm text-muted-foreground">Status: {link.status}</p>
                    </div>
                    {link.status === 'ACCEPTED' && (
                      <Button size="sm" variant="outline" onClick={() => updateMutation.mutate({ linkId: link.id, status: 'REVOKED' })}>Revoke</Button>
                    )}
                  </div>
                ))}
                {links?.filter(l => l.source_workspace_id === currentWorkspace).length === 0 && (
                  <p className="text-muted-foreground">No outbound connections.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
