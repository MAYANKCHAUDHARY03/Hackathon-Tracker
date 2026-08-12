import React, { useState } from 'react'
import { useWorkspaceStore } from '@/store/workspaceStore'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { graphApi, type GraphEdge } from '@/api/graph'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Network, ArrowRight, Activity, CheckCircle, Brain, User, ShieldCheck } from 'lucide-react'

export default function GraphExplorer() {
  const [nodeId, setNodeId] = useState<string>('')
  const [activeNode, setActiveNode] = useState<string>('')

  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['graph', activeNode, workspaceId],
    queryFn: () => graphApi.traverseGraph(workspaceId!, activeNode, 2),
    enabled: !!activeNode && !!workspaceId,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (nodeId) {
      setActiveNode(nodeId)
    }
  }

  const verifyMutation = useMutation({
    mutationFn: (edgeId: string) => graphApi.verifyEdge(workspaceId!, edgeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['graph', activeNode, workspaceId] })
    }
  })

  const handleVerifyEdge = (edgeId: string) => {
    verifyMutation.mutate(edgeId)
  }

  const renderEdgeProvenance = (edge: GraphEdge) => {
    if (!edge.provenance) return null;
    
    switch (edge.provenance) {
      case 'AI-inferred':
        return (
          <div className="flex items-center space-x-2 mt-1">
            <Badge variant="outline" className="border-amber-500 text-amber-500 flex items-center space-x-1 text-[10px]">
              <Brain className="w-3 h-3" />
              <span>AI Inferred ({Math.round((edge.confidence || 0) * 100)}%)</span>
            </Badge>
            <Button 
              size="sm" 
              variant="ghost" 
              className="h-6 px-2 text-xs" 
              onClick={() => handleVerifyEdge(edge.id)}
              disabled={verifyMutation.isPending}
            >
              <CheckCircle className="w-3 h-3 mr-1" />
              Verify
            </Button>
          </div>
        )
      case 'user-provided':
        return (
          <Badge variant="secondary" className="mt-1 flex items-center space-x-1 text-[10px]">
            <User className="w-3 h-3" />
            <span>User Provided</span>
          </Badge>
        )
      case 'verified':
        return (
          <Badge variant="default" className="mt-1 bg-green-600 hover:bg-green-700 flex items-center space-x-1 text-[10px]">
            <ShieldCheck className="w-3 h-3" />
            <span>Verified</span>
          </Badge>
        )
      default:
        return null;
    }
  }

  const renderNodeDetails = (id: string, isCenter = false) => {
    if (!data?.nodes[id]) return null
    const node = data.nodes[id]
    
    // A rudimentary way to guess a label
    const label = node.data.name || node.data.title || node.data.full_name || id
    
    return (
      <Card 
        key={id} 
        className={`cursor-pointer transition-colors hover:border-primary/50 ${isCenter ? 'border-primary ring-1 ring-primary/50 bg-primary/5' : ''}`}
        onClick={() => {
          setNodeId(id)
          setActiveNode(id)
        }}
      >
        <CardHeader className="p-4 pb-2">
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4" />
            <span>{node.type}</span>
          </div>
          <CardTitle className="text-base truncate" title={label}>{label}</CardTitle>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <p className="text-xs text-muted-foreground truncate">{id}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="flex flex-col space-y-6 h-[calc(100vh-8rem)]">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
        <p className="text-muted-foreground">
          Explore relationships between projects, teams, challenges, and organizations.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Navigate Graph</CardTitle>
          <CardDescription>Enter a Node ID (UUID) to start traversing</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex space-x-4">
            <Input 
              placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000" 
              value={nodeId}
              onChange={(e) => setNodeId(e.target.value)}
              className="max-w-md"
            />
            <Button type="submit" disabled={!nodeId}>
              <Network className="mr-2 h-4 w-4" />
              Traverse
            </Button>
          </form>
        </CardContent>
      </Card>

      {isLoading && (
        <div className="flex items-center justify-center p-12">
          <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
        </div>
      )}

      {error && (
        <Card className="border-destructive">
          <CardContent className="p-6 text-destructive">
            Failed to load graph data. Please check the ID and try again.
          </CardContent>
        </Card>
      )}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1 overflow-auto p-2">
          {/* Incoming */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center">Incoming Relationships</h3>
            <div className="space-y-4">
              {data.path.filter(e => e.target_id === activeNode).map((edge) => (
                <div key={edge.id} className="flex flex-col space-y-2">
                  {renderNodeDetails(edge.source_id)}
                  <div className="flex flex-col items-center justify-center text-sm text-muted-foreground py-2">
                    <span className="bg-muted px-2 py-1 rounded-md flex items-center space-x-1">
                      <span>{edge.relation_type}</span>
                      <ArrowRight className="h-3 w-3" />
                    </span>
                    {renderEdgeProvenance(edge)}
                  </div>
                </div>
              ))}
              {data.path.filter(e => e.target_id === activeNode).length === 0 && (
                <p className="text-muted-foreground text-sm">No incoming relationships</p>
              )}
            </div>
          </div>
          
          {/* Center */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Active Node</h3>
            {renderNodeDetails(activeNode, true)}
          </div>

          {/* Outgoing */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center">Outgoing Relationships</h3>
            <div className="space-y-4">
              {data.path.filter(e => e.source_id === activeNode).map((edge) => (
                <div key={edge.id} className="flex flex-col space-y-2">
                  <div className="flex flex-col items-center justify-center text-sm text-muted-foreground py-2">
                    <span className="bg-muted px-2 py-1 rounded-md flex items-center space-x-1">
                      <span>{edge.relation_type}</span>
                      <ArrowRight className="h-3 w-3" />
                    </span>
                    {renderEdgeProvenance(edge)}
                  </div>
                  {renderNodeDetails(edge.target_id)}
                </div>
              ))}
              {data.path.filter(e => e.source_id === activeNode).length === 0 && (
                <p className="text-muted-foreground text-sm">No outgoing relationships</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
