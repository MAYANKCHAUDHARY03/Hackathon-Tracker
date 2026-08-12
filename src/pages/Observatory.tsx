import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useWorkspaceStore } from '@/store/workspaceStore'
import { observatoryApi } from '@/api/observatoryApi'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Globe, Users, Folder, Flag, Briefcase, DollarSign, TrendingUp } from 'lucide-react'

export default function Observatory() {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId)

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['observatoryStats', workspaceId],
    queryFn: () => observatoryApi.getWorkspaceStats(workspaceId!),
    enabled: !!workspaceId,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
      </div>
    )
  }

  if (error || !stats) {
    return (
      <Card className="border-destructive mt-6">
        <CardContent className="p-6 text-destructive">
          Failed to load Observatory data. Please try again later.
        </CardContent>
      </Card>
    )
  }

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
  }

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Globe className="h-8 w-8 text-primary" />
          Global Innovation Observatory
        </h1>
        <p className="text-muted-foreground">
          High-level aggregated view of the ecosystem's innovation metrics. Privacy and aggregation controls strictly enforced.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <Folder className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_projects}</div>
            <p className="text-xs text-muted-foreground">Ideated, built, or deployed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Participants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_participants}</div>
            <p className="text-xs text-muted-foreground">Across all programs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hackathons</CardTitle>
            <Flag className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_hackathons}</div>
            <p className="text-xs text-muted-foreground">Challenges hosted</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Jobs Created</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_jobs_created}</div>
            <p className="text-xs text-muted-foreground">New roles generated</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Funding Raised</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.total_funding_raised)}</div>
            <p className="text-xs text-muted-foreground">Capital secured</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue Generated</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.total_revenue_generated)}</div>
            <p className="text-xs text-muted-foreground">Market traction</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
