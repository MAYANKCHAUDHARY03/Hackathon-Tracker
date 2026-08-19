import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { useWorkspaceStore } from '@/store/workspaceStore'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

// Assuming api structure for org federation
const orgFederationApi = {
  getTrusts: async (orgId: string) => {
    const res = await fetch(`/api/v1/organizations/${orgId}/federation/trusts`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!res.ok) throw new Error('Failed to fetch trusts')
    return res.json()
  },
  proposeTrust: async (orgId: string, data: any) => {
    const res = await fetch(`/api/v1/organizations/${orgId}/federation/trusts`, {
      method: 'POST',
      headers: { 
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to propose trust')
    return res.json()
  },
  acceptTrust: async (orgId: string, trustId: string) => {
    const res = await fetch(`/api/v1/organizations/${orgId}/federation/trusts/${trustId}/accept`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!res.ok) throw new Error('Failed to accept trust')
    return res.json()
  },
  revokeTrust: async (orgId: string, trustId: string) => {
    const res = await fetch(`/api/v1/organizations/${orgId}/federation/trusts/${trustId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!res.ok) throw new Error('Failed to revoke trust')
    return true
  }
}

export default function OrganizationFederation() {
  const currentWorkspace = useWorkspaceStore((state) => state.activeWorkspaceId)
  // Assuming the user needs an org ID. For MVP, we extract it or mock it if they don't have a direct org selector.
  // Actually, we need currentOrgId. We will assume the UI passes or has currentOrgId.
  // We'll use a mocked org ID or ask the user to input their org ID for now.
  const [currentOrgId, setCurrentOrgId] = useState('')
  const queryClient = useQueryClient()
  const [newTrusteeId, setNewTrusteeId] = useState('')
  const [scopes, setScopes] = useState('federated_reviewer')

  const { data: trusts, isLoading } = useQuery({
    queryKey: ['org-federation', currentOrgId],
    queryFn: () => orgFederationApi.getTrusts(currentOrgId),
    enabled: !!currentOrgId,
  })

  const proposeMutation = useMutation({
    mutationFn: (targetId: string) => orgFederationApi.proposeTrust(currentOrgId, { 
      trustee_org_id: targetId, 
      allowed_scopes: scopes.split(',').map(s => s.trim()) 
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-federation', currentOrgId] })
      setNewTrusteeId('')
    },
  })

  const acceptMutation = useMutation({
    mutationFn: (trustId: string) => orgFederationApi.acceptTrust(currentOrgId, trustId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-federation', currentOrgId] })
    },
  })

  const revokeMutation = useMutation({
    mutationFn: (trustId: string) => orgFederationApi.revokeTrust(currentOrgId, trustId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-federation', currentOrgId] })
    },
  })

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Organization Federation</h1>
          <p className="text-muted-foreground mt-2">
            Establish trust relationships with other organizations for cross-tenant roles.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your Organization Context</CardTitle>
        </CardHeader>
        <CardContent>
          <input 
            type="text"
            placeholder="Your Organization ID"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            value={currentOrgId}
            onChange={(e) => setCurrentOrgId(e.target.value)}
          />
        </CardContent>
      </Card>

      {currentOrgId && (
        <>
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
                {isLoading ? (
                  <div>Loading...</div>
                ) : (
                  <div className="space-y-4">
                    {trusts?.filter((t: any) => t.trustee_org_id === currentOrgId).map((trust: any) => (
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
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Outbound Trust (You are Trustor)</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div>Loading...</div>
                ) : (
                  <div className="space-y-4">
                    {trusts?.filter((t: any) => t.trustor_org_id === currentOrgId).map((trust: any) => (
                      <div key={trust.id} className="flex justify-between items-center p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">To Trustee: {trust.trustee_org_id}</p>
                          <p className="text-sm text-muted-foreground">Status: {trust.status}</p>
                          <p className="text-sm text-muted-foreground">Scopes: {trust.allowed_scopes.join(', ')}</p>
                        </div>
                        <Button size="sm" variant="outline" onClick={() => revokeMutation.mutate(trust.id)}>Revoke</Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
