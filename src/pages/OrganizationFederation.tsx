import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { OrganizationTrustManager } from '@/components/enterprise/OrganizationTrustManager'

export default function OrganizationFederation() {
  const [currentOrgId, setCurrentOrgId] = useState('')

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

      {currentOrgId && <OrganizationTrustManager orgId={currentOrgId} />}
    </div>
  )
}
