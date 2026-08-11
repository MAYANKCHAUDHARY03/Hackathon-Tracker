# Knowledge Graph Design — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: Knowledge Graph architecture, relationship model, consumption patterns  
**Purpose**: Define the Knowledge Graph as a relationship layer before implementation

---

## Core Principle

> The Knowledge Graph is a **read/relationship layer over the existing canonical database** (Organizations, Users, Hackathons, Teams, Projects, Challenges, Results) — it is **not** a replacement database. Search, Matching, and AI all consume the relationship layer; they do not become new sources of truth.

This means:
1. Canonical data lives in domain tables (`users`, `projects`, `teams`, etc.)
2. The Knowledge Graph stores **relationships between entities** and **metadata about those relationships**
3. Deleting a GraphEdge does NOT delete the underlying entities
4. GraphEdges are derived/supplementary data — they can be rebuilt from canonical data
5. No business logic should depend on a GraphEdge existing — it should work without the graph (degraded, but functional)

---

## Entity Node Types

The Knowledge Graph treats existing entities as nodes. No separate "node" table is needed — nodes are rows in their canonical tables.

| Node Type | Canonical Table | Key Fields for Graph |
|---|---|---|
| `User` | `users` | id, full_name, email |
| `Organization` | `organizations` | id, name, slug |
| `Workspace` | `workspaces` | id, name, slug |
| `Hackathon` | `hackathons` | id, name, status |
| `Team` | `teams` | id, name, status |
| `Project` | `projects` | id, title, status |
| `Challenge` | `challenges` | id, title, status |
| `Technology` | `technologies` | id, name, category |
| `Person` | `people` | id, full_name |
| `Startup` | `startups` | id, name, industry |
| `Sponsor` | `sponsors` | id, name |
| `Problem` | `problems` (Phase 30) | id, title, domain |
| `ResearchLink` | `research_links` (Phase 31) | id, title, source_url |

---

## Relationship Types (Edge Types)

### Canonical Relationships (auto-created from model events)

| Relation | Source → Target | Provenance | When Created |
|---|---|---|---|
| `contains` | Hackathon → Team | `verified` | Team created in hackathon |
| `contains` | Hackathon → Challenge | `verified` | Challenge created in hackathon |
| `belongs_to` | Workspace → Organization | `verified` | Workspace linked to org |
| `created` | Team → Project | `verified` | Project created by team |
| `member_of` | User → Team | `verified` | TeamMember created |
| `organized_by` | Hackathon → Organization | `verified` | Hackathon created in org workspace |

### User-Provided Relationships

| Relation | Source → Target | Provenance | Description |
|---|---|---|---|
| `solves` | Project → Challenge | `user-provided` | Team claims their project solves a challenge |
| `uses` | Project → Technology | `user-provided` | Technology used in project |
| `mentored_by` | Team → Person | `user-provided` | Mentor assigned to team |
| `evaluated_by` | Project → Person | `user-provided` | Judge evaluated project |
| `inspired_by` | Project → Project | `user-provided` | One project inspired another |
| `evolved_from` | Startup → Project | `user-provided` | Startup evolved from hackathon project |
| `deployed_at` | Project → Organization | `user-provided` | Project deployed at org |

### Imported Relationships

| Relation | Source → Target | Provenance | Description |
|---|---|---|---|
| `cites` | Project → ResearchLink | `imported` | Paper/patent citation |
| `uses_dataset` | Project → ResearchLink | `imported` | Dataset used |
| `contributed_to` | User → Project | `imported` | From external platform (GitHub, etc.) |

### AI-Inferred Relationships

| Relation | Source → Target | Provenance | Description |
|---|---|---|---|
| `similar_to` | Project → Project | `AI-inferred` | Content similarity detected |
| `related_to` | Challenge → Challenge | `AI-inferred` | Related problem domains |
| `expert_in` | User → Technology | `AI-inferred` | Inferred from project history |
| `potential_mentor` | Person → Challenge | `AI-inferred` | Expertise match |

**Rule**: AI-inferred edges always have:
- `provenance = "AI-inferred"`
- `confidence` score (0.0–1.0)
- Cannot be promoted to `verified` without human action

---

## GraphEdge Schema (Phase 28 Evolution)

```python
class GraphEdge(BaseEntity):
    __tablename__ = "graph_edges"

    workspace_id       # UUID FK → workspaces (tenant scope)
    
    source_type        # String: node type (e.g., "Project")
    source_id          # UUID: node ID in canonical table
    
    target_type        # String: node type (e.g., "Challenge")
    target_id          # UUID: node ID in canonical table
    
    relation_type      # String: one of the defined relationship types
    
    # NEW in Phase 28
    provenance         # Enum: verified | user-provided | imported | AI-inferred
    confidence         # Float: 0.0–1.0 (1.0 for verified, variable for AI-inferred)
    
    created_by         # UUID FK → users (who created this edge)
    verified_at        # DateTime (when verified, if applicable)
    verified_by        # UUID FK → users (who verified, if applicable)
    
    properties         # JSON: edge-specific metadata
    metadata           # JSON: additional context (AI model, import source, etc.)
```

---

## Consumption Patterns

### 1. Search (Phase 29)
```
User query → keyword + semantic matches → for each result, fetch 1-hop graph context
→ enrich result with: related entities, technologies, teams
→ match_reasons includes "connected to X via Y relationship"
```

### 2. Matching (existing + Phase 28 enhancement)
```
User/Team profile → graph neighbors → compute similarity scores
→ rank by: shared technologies, common challenges, related projects
```

### 3. AI Copilot (Phase 37)
```
User question → intent detection → permission check
→ Knowledge Graph traversal (scoped to user's permissions)
→ Verified data only (provenance != "AI-inferred" for factual claims)
→ AI reasoning over verified data
→ Answer with evidence (source entities from graph)
```

### 4. Analytics/Dashboards (Phase 36)
```
Org admin → aggregate graph metrics per workspace
→ e.g., "How many projects used React?" = COUNT edges where relation=uses AND target_type=Technology AND target_name=React
```

### 5. Impact Measurement (Phase 39)
```
Track lifecycle progression through graph edges:
Project → evolved_from → Startup (graph edge)
Startup status → active/funded/exited (canonical data)
→ Funnel: Projects → Prototypes → Pilots → Deployments → Startups → Impact
```

---

## Permission Model for Graph Access

| Caller | Can See |
|---|---|
| Workspace Member | All edges in their workspace |
| Workspace Admin | All edges + can create/edit/delete |
| API Consumer (Phase 32) | Edges within their authorized scopes |
| Federation Partner (Phase 41) | Only edges on FederatedResources with active agreement |
| Public/Anonymous | Only edges where both nodes have `visibility=public` |

---

## Data Integrity Rules

1. **Orphan prevention**: When a canonical entity is deleted (soft or hard), associated edges should be soft-deleted (archived) but not hard-deleted immediately.

2. **Unique constraint**: `(source_id, relation_type, target_id)` remains unique — no duplicate edges.

3. **Bidirectional edges**: Some relationships are inherently directional (`created_by`) while others could be traversed either way (`similar_to`). The graph service will handle both directions in traversal.

4. **Provenance immutability**: An edge's provenance can be upgraded (`AI-inferred` → `user-provided` → `verified`) but never downgraded.

---

## Conclusion

The Knowledge Graph design is ready for Phase 28 implementation. It:
- ✅ Respects the core principle (relationship layer, not replacement DB)
- ✅ Defines all relationship types with provenance
- ✅ Specifies consumption patterns for Search, Matching, AI
- ✅ Enforces AI guardrails (AI-inferred edges clearly labeled)
- ✅ Maintains tenant isolation via `workspace_id`
- ✅ Supports the full V5.0 lifecycle
