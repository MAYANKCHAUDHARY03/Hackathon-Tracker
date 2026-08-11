# Data Ownership Audit — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: All tenant-scoped data, ownership model, cross-tenant isolation  
**Purpose**: Verify every entity has proper tenant scoping and ownership

---

## 1. Tenant Isolation Model

The platform uses **Workspace-based multi-tenancy**:
- `Workspace` is the primary isolation boundary
- `Organization` groups Workspaces but does not bypass Workspace isolation
- All data queries must filter by `workspace_id`
- Cross-workspace data access is forbidden at the service layer

### Tenant Scoping Verification

| Entity | Has `workspace_id`? | Isolation Method | ✅/⚠️ |
|---|---|---|---|
| Hackathon | ✅ Direct | workspace FK | ✅ |
| Team | ✅ Direct | workspace FK | ✅ |
| TeamMember | ❌ Indirect | via Team | ⚠️ |
| Project | ✅ Direct | workspace FK | ✅ |
| Technology | ❌ Global | shared resource | ✅ (by design) |
| Challenge | ✅ Direct | workspace FK | ✅ |
| Person | ✅ Direct | workspace FK | ✅ |
| MentorAssignment | ✅ Direct | workspace FK | ✅ |
| JudgeAssignment | ✅ Direct | workspace FK | ✅ |
| EvaluationTemplate | ✅ Direct | workspace FK | ✅ |
| Evaluation | ✅ Direct | workspace FK | ✅ |
| HackathonResult | ✅ Direct | workspace FK | ✅ |
| Reward | ✅ Direct | workspace FK | ✅ |
| Achievement | ✅ Direct | workspace FK | ✅ |
| KanbanBoard | ✅ Direct | workspace FK | ✅ |
| Task | ❌ Indirect | via Board | ⚠️ |
| Notification | ✅ Direct | workspace FK | ✅ |
| ActivityEvent | ✅ Direct | workspace FK | ✅ |
| AuditLog | ✅ Direct | workspace FK | ✅ |
| GraphEdge | ✅ Direct | workspace FK | ✅ |
| Sponsor | ✅ Direct | workspace FK | ✅ |
| Startup | ✅ Direct | workspace FK | ✅ |
| HackathonRound | ❌ Indirect | via Hackathon | ⚠️ |
| Deadline | ❌ Indirect | via Round | ⚠️ |
| SubmissionRequirement | ❌ Indirect | via Round | ⚠️ |
| RoundSubmission | ❌ Indirect | via Round | ⚠️ |
| SubmissionItem | ❌ Indirect | via Submission | ⚠️ |
| EvaluationScore | ❌ Indirect | via Evaluation | ✅ |
| ProjectUpdate | ❌ Indirect | via Project | ⚠️ |
| ProjectDocument | ❌ Indirect | via Project | ⚠️ |
| ProjectFunding | ❌ Indirect | via Project | ⚠️ |

### ⚠️ Indirect Isolation Analysis

Entities marked ⚠️ lack a direct `workspace_id` and rely on JOINs to parent entities for tenant filtering. This is **acceptable but requires careful query construction** — all service methods for these entities MUST join through their parent to enforce workspace scoping.

**Risk assessment**: Low. Parent entities enforce workspace scoping via FK cascades. No cross-tenant leakage is possible unless a query bypasses the parent join.

---

## 2. Ownership Model

### Who Creates, Owns, Reads, Writes, Deletes

| Entity | Creator | Owner | Read Access | Write Access | Delete |
|---|---|---|---|---|---|
| Workspace | Any User | Owner/Admin | Members | Owner/Admin | Owner |
| Organization | Any User | Owner/Admin | Members | Owner/Admin | Owner |
| Hackathon | WS Admin | Workspace | WS Members | WS Admin | WS Admin |
| Team | Team Creator | Workspace | WS Members | Lead/Co-lead | WS Admin |
| Project | Team Lead | Team | WS Members | Team Members | WS Admin |
| Challenge | WS Admin | Workspace | WS Members | WS Admin | WS Admin |
| Evaluation | Judge/Person | Workspace | WS Admin + Evaluator | Evaluator (until locked) | WS Admin |
| HackathonResult | WS Admin | Workspace | WS Members | WS Admin | WS Admin |
| Achievement | System/Admin | Workspace | Owner + WS Admin | WS Admin | WS Admin |
| Person | WS Member | Workspace | Per visibility setting | Creator + Admin | WS Admin |
| GraphEdge | System/User | Workspace | WS Members | Edge creator + Admin | WS Admin |
| Notification | System | User | Target user | System | User (dismiss) |

---

## 3. Cross-Tenant Leakage Vectors

### Identified Risks

1. **GraphEdge traversal**: `traverse()` in `GraphQueryService` filters by `workspace_id` ✅ — no cross-workspace traversal possible.

2. **Search service**: `search()` in `SearchService` filters by `workspace_id` ✅ — results scoped to workspace.

3. **Technology table**: Global (no workspace_id). This is by design — technologies are shared reference data (React, Python, etc.). **No risk**.

4. **User table**: Global. Users can be members of multiple workspaces. User data itself is not workspace-scoped. **Acceptable** — user profile data is personal, not workspace data.

5. **Organization**: Acts as an umbrella but does not grant cross-workspace data access. `OrganizationMembership` only controls org-level admin functions. ✅

### V5.0 New Risks

| Phase | Risk | Mitigation |
|---|---|---|
| 30 (Challenge Exchange) | Challenges visible across workspaces | Only challenges with `visibility=public` + `ecosystem_opt_in=true` |
| 35 (Passport) | User profile aggregates cross-workspace data | User controls visibility; aggregation runs per-user auth |
| 40 (Observatory) | Cross-org aggregated data | Only permissioned via `ecosystem_opt_in`; aggregation anonymized |
| 41 (Federation) | Cross-org resource sharing | FederationAgreement model; read-only cross-references only |

---

## 4. Conclusion

Data ownership is **well-structured**. All core entities carry `workspace_id` directly or through mandatory parent relationships. The V5.0 phases that introduce cross-tenant visibility (30, 35, 40, 41) will use explicit opt-in mechanisms and never bypass workspace isolation.
