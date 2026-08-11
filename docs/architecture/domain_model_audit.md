# Domain Model Audit — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: All 32 SQLAlchemy models  
**Purpose**: Map every entity, validate naming, identify gaps for V5.0 lifecycle

---

## 1. Current Entity Inventory

### Core Entities (Multi-Tenant Scoped)
| Entity | Table | Tenant FK | Owner FK | Status |
|---|---|---|---|---|
| Workspace | `workspaces` | self (root) | org FK | ✅ |
| Organization | `organizations` | self (root) | — | ✅ |
| OrganizationMembership | `organization_memberships` | org FK | user FK | ✅ |
| User | `users` | — (global) | — | ✅ |
| WorkspaceMembership | `workspace_memberships` | workspace FK | user FK | ✅ |

### Hackathon Lifecycle
| Entity | Table | Tenant FK | Status |
|---|---|---|---|
| Hackathon | `hackathons` | `workspace_id` | ✅ |
| Team | `teams` | `workspace_id` | ✅ |
| TeamMember | `team_members` | via Team | ✅ |
| Project | `projects` | `workspace_id` | ✅ |
| Technology | `technologies` | — (global) | ✅ |
| ProjectTechnology | `project_technologies` | via Project | ✅ |
| Challenge | `challenges` | `workspace_id` | ✅ |

### Evaluation & Outcomes
| Entity | Table | Tenant FK | Status |
|---|---|---|---|
| EvaluationTemplate | `evaluation_templates` | `workspace_id` | ✅ |
| EvaluationCriterion | `evaluation_criteria` | `workspace_id` | ✅ |
| Evaluation | `evaluations` | `workspace_id` | ✅ |
| EvaluationScore | `evaluation_scores` | via Evaluation | ✅ |
| HackathonResult | `hackathon_results` | `workspace_id` | ✅ |
| Reward | `rewards` | `workspace_id` | ✅ |
| Achievement | `achievements` | `workspace_id` | ✅ |

### People & Roles
| Entity | Table | Tenant FK | Status |
|---|---|---|---|
| Person | `people` | `workspace_id` | ✅ |
| MentorAssignment | `mentor_assignments` | `workspace_id` | ✅ |
| JudgeAssignment | `judge_assignments` | `workspace_id` | ✅ |

### Workflow & Collaboration
| Entity | Table | Tenant FK | Status |
|---|---|---|---|
| HackathonRound | `hackathon_rounds` | via Hackathon | ✅ |
| Deadline | `deadlines` | via Round | ✅ |
| RoundProgress | `round_progress` | via Round | ✅ |
| SubmissionRequirement | `submission_requirements` | via Round | ✅ |
| RoundSubmission | `round_submissions` | via Round | ✅ |
| SubmissionItem | `submission_items` | via Submission | ✅ |
| KanbanBoard | `kanban_boards` | `workspace_id` | ✅ |
| KanbanColumn | `kanban_columns` | via Board | ✅ |
| Task | `tasks` | via Board | ✅ |

### Supporting
| Entity | Table | Tenant FK | Status |
|---|---|---|---|
| Notification | `notifications` | `workspace_id` | ✅ |
| ActivityEvent | `activity_events` | `workspace_id` | ✅ |
| AuditLog | `audit_logs` | `workspace_id` | ✅ |
| Feedback | `feedbacks` | `workspace_id` | ✅ |
| ApplicationForm | `application_forms` | via Hackathon | ✅ |
| ApplicationSubmission | `application_submissions` | via Form | ✅ |
| Sponsor | `sponsors` | `workspace_id` | ✅ |
| Startup | `startups` | `workspace_id` | ✅ |

### Integration & Auth
| Entity | Table | Status |
|---|---|---|
| WorkspaceIntegration | `workspace_integrations` | ✅ |
| WebhookSubscription | `webhook_subscriptions` | ✅ |
| WebhookDelivery | `webhook_deliveries` | ✅ |
| IdentityProvider | `identity_providers` | ✅ |
| ExternalIdentity | `external_identities` | ✅ |
| ScimToken | `scim_tokens` | ✅ |
| CalendarIntegration | `calendar_integrations` | ✅ |
| AutomationRule | `automation_rules` | ✅ |
| AutomationExecution | `automation_executions` | ✅ |

### Graph
| Entity | Table | Status |
|---|---|---|
| GraphEdge | `graph_edges` | ✅ (needs evolution) |

### Incubation
| Entity | Table | Status |
|---|---|---|
| ProjectUpdate | `project_updates` | ✅ |
| ProjectDocument | `project_documents` | ✅ |
| ProjectFunding | `project_funding` | ✅ |

---

## 2. Target V5.0 Lifecycle

```
Problem → Challenge → Hackathon → Idea → Team → Prototype → Validation →
Incubation → Startup/Product → Pilot → Deployment → Impact → Knowledge → New Problems
```

### Missing Entities for V5.0

| Entity | Phase | Purpose |
|---|---|---|
| **Problem** | 30 | Root of lifecycle: real-world problems that drive challenges |
| **ResearchLink** | 31 | Links projects to papers, patents, datasets, repos |
| **OAuthApp** | 32 | Third-party API consumer registration |
| **APIKey** | 32 | Per-app API key management |
| **APIUsageLog** | 32 | Rate limiting and usage analytics |
| **InnovationSchema** | 33 | Versioned data exchange schemas |
| **DataExport/Import** | 33 | Export/import tracking |
| **VerificationRecord** | 34 | Verified achievements with human verifier |
| **InnovationPassport** | 35 | User-controlled portable profile |
| **ImpactMetric** | 39 | Custom impact measurement definitions |
| **ImpactRecord** | 39 | Full funnel tracking records |
| **FederationAgreement** | 41 | Cross-org sharing agreement |
| **FederatedResource** | 41 | Cross-tenant read-only references |
| **GovernancePolicy** | 44 | Data residency, retention, consent |
| **ConsentRecord** | 44 | User consent tracking |

---

## 3. Naming Consistency Issues

| Issue | Current | Recommendation |
|---|---|---|
| Hackathon `organiser` field | British spelling | Keep as-is (non-breaking) |
| `Person` vs `User` distinction | `Person` is external mentors/judges, `User` is platform users | ✅ Correct, document explicitly |
| `Startup` lacks `project_id` FK | No direct link to source project | Add in Phase 28 via GraphEdge |
| `Challenge.hackathon_id` is NOT NULL | Can't have standalone challenges | Fix in Phase 30 (make nullable) |

---

## 4. Relationship Gaps

- **Team → User**: `TeamMember` exists but graph event is a no-op (workspace_id unavailable)
- **Project → Challenge**: No FK, only possible through GraphEdge
- **Hackathon → Organization**: Indirect via Workspace → Organization
- **Achievement → Verification**: No link exists (Phase 34 will add)
- **Startup → Project**: No FK, only GraphEdge with `evolved_from`

**All of these will be resolved through the Knowledge Graph (Phase 28) rather than adding direct FKs**, following the principle that the graph is a relationship layer over canonical data.

---

## 5. Conclusion

The domain model is **solid for current functionality** but needs the entities listed in §2 to support the V5.0 lifecycle. The Knowledge Graph will bridge existing relationship gaps without requiring schema-breaking FK additions to established tables.
