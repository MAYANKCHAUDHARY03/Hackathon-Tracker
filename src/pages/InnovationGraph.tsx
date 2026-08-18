import React, { useState, useCallback, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState, MarkerType, Position } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { networkApi, type NetworkNode, type NetworkEdge } from '@/api/networkApi';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, Search, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

// Basic mapping of node types to colors/styles
const nodeTypeColors: Record<string, string> = {
  challenge: '#ff9999',
  project: '#99ccff',
  impact: '#99ff99',
  user: '#ffcc99',
  organization: '#cc99ff',
  default: '#e2e8f0',
};

export default function InnovationGraph() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const workspaceId = activeWorkspaceId;
  
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('Ocean Clean');
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['network-resolve', workspaceId, searchQuery],
    queryFn: () => networkApi.resolveNetwork(workspaceId!, { query: searchQuery, include_impact_metrics: true }),
    enabled: !!workspaceId && !!searchQuery,
  });

  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);

  useEffect(() => {
    if (data) {
      // Very simple horizontal layout
      const newNodes = data.nodes.map((node, index) => {
        let x = 100;
        let y = 100 + index * 100;
        
        // rudimentary layout based on type
        if (node.type === 'challenge') { x = 100; y = 200; }
        if (node.type === 'project') { x = 400; y = 200; }
        if (node.type === 'impact') { x = 700; y = 200; }

        return {
          id: node.id,
          position: { x, y },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          data: { 
            label: (
              <div className="flex flex-col items-center p-2 text-center w-32">
                <Badge variant="outline" className="mb-1 text-[10px]">{node.type.toUpperCase()}</Badge>
                <div className="font-bold text-sm">{node.name}</div>
                {node.metadata && Object.entries(node.metadata).map(([k, v]) => (
                  <div key={k} className="text-[10px] text-muted-foreground mt-1">{k}: {v}</div>
                ))}
              </div>
            ) 
          },
          style: {
            background: nodeTypeColors[node.type] || nodeTypeColors.default,
            color: '#000',
            border: '1px solid #222',
            borderRadius: '8px',
            width: 150,
          }
        };
      });

      const newEdges = data.edges.map(edge => ({
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        label: edge.relation,
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
        style: { stroke: '#888' },
      }));

      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [data, setNodes, setEdges]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchQuery(query);
    }
  };

  if (!workspaceId) {
    return <div className="p-8">Select a workspace to view the Innovation Graph.</div>;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="p-4 border-b flex items-center justify-between bg-card">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Innovation Network</h1>
          <p className="text-sm text-muted-foreground">
            Visualize the lifecycle of innovation from Problem to Impact.
          </p>
        </div>
        
        <form onSubmit={handleSearch} className="flex gap-2 items-center">
          <Input 
            placeholder="Search network (e.g. 'Ocean Clean')" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-64"
          />
          <Button type="submit" disabled={isLoading}>
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
            Resolve
          </Button>
        </form>
      </div>

      <div className="flex-1 relative flex">
        <div className="flex-1 h-full border-r">
          {error ? (
            <div className="flex h-full items-center justify-center text-destructive">
              Error loading network graph.
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              colorMode="dark"
            >
              <Controls />
              <MiniMap />
              <Background gap={12} size={1} />
            </ReactFlow>
          )}
        </div>

        {/* AI Insight Sidebar */}
        <div className="w-80 p-4 overflow-y-auto bg-muted/20">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-500" />
                Network Intelligence
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                  <Loader2 className="w-8 h-8 animate-spin mb-4" />
                  <span className="text-sm">Synthesizing network...</span>
                </div>
              ) : data?.ai_summary ? (
                <div className="prose prose-sm dark:prose-invert">
                  {data.ai_summary}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No AI insights generated for this view.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
