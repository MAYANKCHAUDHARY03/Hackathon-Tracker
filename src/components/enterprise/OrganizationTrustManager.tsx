import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { apiClient } from '@/lib/api-client'

export function OrganizationTrustManager({ orgId }: { orgId: string }) {
  const queryClient = useQueryClient()
  const [newTrusteeId, setNewTrusteeId] = useState('')
  const [scopes, setScopes] = useState('federated_reviewer')

  const { data: trusts, isLoading } = useQuery({
    queryKey: ['org-federation', orgId],
    queryFn: () => apiClient.get(`/organizations/${orgId}/federation/trusts`),
    enabled: !!orgId,
  })

  const proposeMutation = useMutation({
    mutationFn: (targetId: string) => apiClient.post(`/organizations/${orgId}/federation/trusts`, { 
      trustee_org_id: targetId, 
      allowed_scopes: scopes.split(',').map(s => s.trim()) 
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-federation', orgId] })
      setNewTrusteeId('')
    },
  })

  const acceptMutation = useMutation({
    mutationFn: (trustId: string) => apiClient.post(`/organizations/${orgId}/federation/trusts/${trustId}/accept`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-federation', orgId] })
    },
  })

  const revokeMutation = useMutation({
    mutationFn: (trustId: string) => apiClient.delete(`/organizations/${orgId}/federation/trusts/${trustId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-federation', orgId] })
    },
  })

  if (isLoading) {
    return <div>Loading trust relationships...</div>
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Propose Trust</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <input 
              type="text"
              placeholder="Trustee Organization ID"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={newTrusteeId}
              onChange={(e) => setNewTrusteeId(e.target.value)}
            />
            <input 
              type="text"
              placeholder="Scopes (comma separated)"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={scopes}
              onChange={(e) => setScopes(e.target.value)}
            />
            <Button 
              onClick={() => proposeMutation.mutate(newTrusteeId)}
              disabled={!newTrusteeId || proposeMutation.isPending}
            >
              Request Trust
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Inbound Requests (You are Trustee)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {trusts?.filter((t: any) => t.trustee_org_id === orgId).map((trust: any) => (
                <div key={trust.id} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">From Trustor: {trust.trustor_org_id}</p>
                    <p className="text-sm text-muted-foreground">Status: {trust.status}</p>
                    <p className="text-sm text-muted-foreground">Scopes: {trust.allowed_scopes.join(', ')}</p>
                  </div>
                  {trust.status === 'pending' && (
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => acceptMutation.mutate(trust.id)}>Accept</Button>
                      <Button size="sm" variant="outline" onClick={() => revokeMutation.mutate(trust.id)}>Reject</Button>
                    </div>
                  )}
                  {trust.status === 'active' && (
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => revokeMutation.mutate(trust.id)}>Revoke</Button>
                    </div>
                  )}
                </div>
              ))}
              {(!trusts || trusts.filter((t: any) => t.trustee_org_id === orgId).length === 0) && (
                <p className="text-muted-foreground text-sm">No inbound requests.</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Outbound Trust (You are Trustor)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {trusts?.filter((t: any) => t.trustor_org_id === orgId).map((trust: any) => (
                <div key={trust.id} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">To Trustee: {trust.trustee_org_id}</p>
                    <p className="text-sm text-muted-foreground">Status: {trust.status}</p>
                    <p className="text-sm text-muted-foreground">Scopes: {trust.allowed_scopes.join(', ')}</p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => revokeMutation.mutate(trust.id)}>Revoke</Button>
                </div>
              ))}
              {(!trusts || trusts.filter((t: any) => t.trustor_org_id === orgId).length === 0) && (
                <p className="text-muted-foreground text-sm">No outbound trust relationships.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
