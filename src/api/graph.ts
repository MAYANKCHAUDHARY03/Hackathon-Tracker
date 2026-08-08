import { apiClient as api } from '@/lib/api-client'

export interface GraphEdge {
  id: string
  source_type: string
  source_id: string
  target_type: string
  target_id: string
  relation_type: string
  properties?: Record<string, any>
}

export interface GraphNode {
  type: string
  data: Record<string, any>
}

export interface GraphTraversalResult {
  path: GraphEdge[]
  nodes: Record<string, GraphNode>
}

export const graphApi = {
  traverseGraph: async (workspaceId: string, nodeId: string, depth: number = 2) => {
    const result = await api.get<GraphTraversalResult>(`/workspaces/${workspaceId}/graph/traverse/${nodeId}?depth=${depth}`)
    return result
  },
}
