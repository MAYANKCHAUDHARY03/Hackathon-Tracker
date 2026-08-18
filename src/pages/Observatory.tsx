import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useWorkspaceStore } from '@/store/workspaceStore'
import { observatoryApi } from '@/api/observatoryApi'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Globe, Users, Folder, Flag, Briefcase, DollarSign, TrendingUp, AlertCircle, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Observatory() {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId)
  const [activeLevel, setActiveLevel] = useState<string | null>(null)

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['observatoryStats', workspaceId],
    queryFn: () => observatoryApi.getWorkspaceStats(workspaceId!),
    enabled: !!workspaceId && !activeLevel,
  })

  const { data: drilldown, isLoading: isDrilldownLoading } = useQuery({
    queryKey: ['observatoryDrilldown', workspaceId, activeLevel],
    queryFn: () => observatoryApi.getDrilldown(workspaceId!, activeLevel!),
    enabled: !!workspaceId && !!activeLevel,
  })

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
  }

  const renderDrilldown = () => {
    if (isDrilldownLoading) {
      return (
        <div className="flex items-center justify-center p-12 mt-6">
          <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
        </div>
      )
    }

    if (!drilldown) return null;

    return (
      <div className="space-y-6 mt-6 animate-in fade-in zoom-in-95">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => setActiveLevel(null)} className="gap-2">
            <ArrowLeft className="h-4 w-4" /> Back to Overview
          </Button>
          <h2 className="text-2xl font-semibold capitalize">{drilldown.level} Insights</h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {drilldown.nodes.map((node: any) => (
            <Card key={node.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{node.name}</CardTitle>
                  <span className={`text-sm font-medium ${node.trend_percentage >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {node.trend_percentage >= 0 ? '+' : ''}{node.trend_percentage.toFixed(1)}%
                  </span>
                </div>
                <CardDescription>Value: {node.value}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={node.time_series}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="date" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
                      <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const renderContent = () => {
    if (!workspaceId) {
      return (
        <Card className="mt-6 border-muted bg-muted/50">
          <CardContent className="flex flex-col items-center justify-center p-12 text-center">
            <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold">No Workspace Selected</h3>
            <p className="text-muted-foreground mt-2">
              Please select a workspace from the sidebar to view its observatory data.
            </p>
          </CardContent>
        </Card>
      )
    }

    if (activeLevel) {
      return renderDrilldown()
    }

    if (isLoading) {
      return (
        <div className="flex items-center justify-center p-12 mt-6">
          <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
        </div>
      )
    }

    if (error || !stats) {
      return (
        <Card className="border-destructive mt-6">
          <CardContent className="p-6 text-destructive flex items-center justify-center">
            Failed to load Observatory data. Please try again later.
          </CardContent>
        </Card>
      )
    }

    return (
      <div className="space-y-8 mt-6">
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

        <div>
          <h3 className="text-lg font-semibold mb-4">Explore Insights</h3>
          <div className="flex flex-wrap gap-4">
            <Button variant="outline" onClick={() => setActiveLevel('technology')}>Explore by Technology</Button>
            <Button variant="outline" onClick={() => setActiveLevel('geography')}>Explore by Geography</Button>
            <Button variant="outline" onClick={() => setActiveLevel('domain')}>Explore by Domain</Button>
            <Button variant="outline" onClick={() => setActiveLevel('outcome')}>Explore by Outcome</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Globe className="h-8 w-8 text-primary" />
          Global Innovation Observatory 2.0
        </h1>
        <p className="text-muted-foreground">
          Predictive, explorable insights across technology, geography, and outcomes with time-series trend analysis.
        </p>
      </div>

      {renderContent()}
    </div>
  )
}

