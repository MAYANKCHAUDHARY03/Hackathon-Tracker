# Performance Audit — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: Query patterns, indexes, N+1 problems, scalability  
**Purpose**: Identify performance risks before adding 18 new phases

---

## 1. Current Index Coverage

### Well-Indexed Entities ✅
All major entities have indexes on:
- `workspace_id` (tenant scoping)
- `status` (filtering)
- Primary keys (auto)
- Foreign keys (query joins)
- `slug`/`name` (lookup)

### GraphEdge Indexes
```python
Index("ix_graph_edges_source", "source_type", "source_id")
Index("ix_graph_edges_target", "target_type", "target_id")
Index("ix_graph_edges_relation", "source_id", "relation_type", "target_id", unique=True)
```
**Assessment**: Good for single-hop queries. Multi-hop BFS traversal (used in `traverse()`) does N queries per depth level — this is acceptable for depth ≤ 3 but will degrade at scale.

---

## 2. N+1 Query Patterns

### Identified N+1 Issues

#### 2.1 Graph Traversal (`GraphQueryService.traverse`)
```python
# Line 104-127: BFS loop with per-node edge queries
while queue:
    current_id, current_depth = queue.pop(0)
    edges = await self.get_edges(current_id, workspace_id, direction="both")  # 1 query per node
```
**Impact**: For a graph with branching factor B and depth D, this executes ~B^D queries.  
**Mitigation for Phase 28**: Batch edge fetching — collect all node IDs per level, then do a single `WHERE source_id IN (...)` query.

#### 2.2 Graph Node Hydration (`GraphQueryService.traverse`)
```python
# Line 137-151: Per-node hydration
for node_str_id, info in nodes_dict.items():
    node = await self.get_node_by_type_and_id(info["type"], info["id"])  # 1 query per node
```
**Impact**: O(N) queries for N nodes in traversal result.  
**Mitigation for Phase 28**: Group nodes by type, batch-fetch each type with `WHERE id IN (...)`.

#### 2.3 Search Service Graph Context
```python
# Line 147-166: Per-result graph traversal
for result in results[:15]:
    graph_data = await graph_service.traverse(start_id=result.id, ...)  # Full traversal per result
```
**Impact**: Up to 15 × (traversal queries) per search.  
**Mitigation for Phase 29**: Cache frequently accessed graph neighborhoods; limit to depth=1.

#### 2.4 Workspace Portfolio (`get_workspace_portfolio`)
```python
# Line 170-208: Loads ALL edges for workspace, then filters in Python
edge_stmt = select(GraphEdge).where(GraphEdge.workspace_id == workspace_id)
edges = (await self.db.execute(edge_stmt)).scalars().all()
```
**Impact**: Loads entire edge table for workspace into memory.  
**Mitigation**: Use `GROUP BY` + `COUNT` SQL aggregation instead of Python filtering.

---

## 3. Missing Indexes for V5.0

| Phase | Table | Column(s) | Reason |
|---|---|---|---|
| 28 | `graph_edges` | `workspace_id, relation_type` | Filter edges by type within workspace |
| 28 | `graph_edges` | `provenance` | Filter by provenance status |
| 29 | `content_embeddings` | `entity_type, entity_id` | Embedding lookup |
| 29 | Content tables | Full-text search (GIN) on `description`, `problem_statement` | Keyword search performance |
| 30 | `challenges` | `visibility, status` | Public challenge discovery |
| 32 | `api_keys` | `key_hash` | API key lookup on every request |
| 32 | `api_usage_logs` | `app_id, created_at` | Usage analytics queries |
| 34 | `verification_records` | `entity_type, entity_id, status` | Verification status lookup |
| 39 | `impact_records` | `workspace_id, stage, created_at` | Funnel analytics |

---

## 4. Query Pattern Assessment for V5.0

| Phase | Expected Query Pattern | Concern Level |
|---|---|---|
| 28 (Knowledge Graph) | Multi-hop traversal, relationship CRUD | 🟠 Batch optimization needed |
| 29 (Semantic Search) | Vector similarity + keyword + graph | 🔴 Most complex query pipeline |
| 30 (Challenge Exchange) | Cross-workspace discovery (opt-in) | 🟡 Index on visibility |
| 32 (Open API) | Per-request auth check | 🔴 Must be < 5ms |
| 36 (Org Intelligence) | Aggregation dashboards | 🟠 Use SQL aggregation, not Python |
| 37 (AI Copilot) | Graph + search + AI | 🟠 Cache graph context |
| 40 (Observatory) | Cross-org aggregation | 🟡 Pre-compute aggregates |

---

## 5. Recommendations

1. **Phase 28**: Rewrite `traverse()` to batch-fetch edges per depth level
2. **Phase 28**: Rewrite node hydration to batch by entity type
3. **Phase 29**: Add GIN indexes for full-text search if using PostgreSQL
4. **Phase 32**: Use Redis/in-memory cache for API key validation
5. **Phase 36/40**: Pre-compute dashboard aggregates on write (materialized views or event-driven)

---

## 6. Conclusion

The main performance concern is the N+1 pattern in graph traversal (§2.1, §2.2) and per-result graph context hydration in search (§2.3). These will be addressed in Phase 28 as part of the Knowledge Graph evolution. The rest of the application has appropriate indexing and query patterns.
