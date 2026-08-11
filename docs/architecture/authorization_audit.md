# Authorization Audit — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: All 40 router files, dependency guards, permission model  
**Purpose**: Map every endpoint to required permissions and identify gaps

---

## 1. Authorization Framework

The platform uses a **dependency injection authorization model**:

| Guard | Defined In | What It Checks |
|---|---|---|
| `get_current_user` | `dependencies.py` | Valid JWT → active User |
| `verify_workspace_access` | `dependencies.py` | User has WorkspaceMembership in target workspace |
| `require_workspace_admin` | `dependencies.py` | Membership role is `owner` or `admin` |
| `verify_team_access` | `dependencies.py` | User has TeamMember record for target team |
| `require_team_lead_or_colead` | `dependencies.py` | TeamMember `authorization_role` is `lead` or `co_lead` |
| `require_team_lead` | `dependencies.py` | TeamMember `authorization_role` is `lead` |

---

## 2. Endpoint → Permission Matrix

### Auth & User Endpoints
| Endpoint | Guard | Status |
|---|---|---|
| `POST /auth/login` | None (public) | ✅ |
| `POST /auth/register` | None (public) | ✅ |
| `GET /users/me` | `get_current_user` | ✅ |

### Workspace Endpoints
| Endpoint | Guard | Status |
|---|---|---|
| `POST /workspaces` | `get_current_user` | ✅ |
| `GET /workspaces/{id}` | `verify_workspace_access` | ✅ |
| `PUT /workspaces/{id}` | `require_workspace_admin` | ✅ |

### Hackathon Endpoints
| Endpoint | Guard | Status |
|---|---|---|
| `GET .../hackathons` | `verify_workspace_access` | ✅ |
| `POST .../hackathons` | `require_workspace_admin` | ✅ |
| `PUT .../hackathons/{id}` | `require_workspace_admin` | ✅ |
| `DELETE .../hackathons/{id}` | `require_workspace_admin` | ✅ |

### Team Endpoints
| Endpoint | Guard | Status |
|---|---|---|
| `GET .../teams` | `verify_workspace_access` | ✅ |
| `POST .../teams` | `verify_workspace_access` | ✅ |
| `PUT .../teams/{id}` | `verify_team_access` | ✅ |
| `DELETE .../teams/{id}` | `require_workspace_admin` | ✅ |

### Graph Endpoints
| Endpoint | Guard | Status |
|---|---|---|
| `POST .../graph/edges` | `verify_workspace_access` | ✅ |
| `GET .../graph/traverse/{id}` | `verify_workspace_access` | ✅ |

### AI/Intelligence Endpoints
| Endpoint | Guard | Status |
|---|---|---|
| `POST /intelligence/...` | `verify_workspace_access` | ✅ |
| `POST /ai/...` | `verify_workspace_access` | ✅ |

### Search
| Endpoint | Guard | Status |
|---|---|---|
| `GET .../search` | `verify_workspace_access` | ✅ |

### Webhooks
| Endpoint | Guard | Status |
|---|---|---|
| `POST .../webhooks` | `require_workspace_admin` | ✅ |
| `GET .../webhooks` | `verify_workspace_access` | ✅ |

### SCIM
| Endpoint | Guard | Status |
|---|---|---|
| `GET /scim/v2/Users` | Bearer Token (SCIM token) | ✅ |

---

## 3. Identified Gaps

### Current Issues (pre-V5.0)
1. **No organization-level permissions**: `OrganizationMembership.role` exists but no guard dependency uses it. Phases 36 (Org Intelligence) and 40 (Observatory) will need an `require_org_admin` guard.

2. **No per-entity ownership check**: For example, editing a project doesn't verify the current user is on the project's team — it only checks workspace membership. This is acceptable for small workspaces but may need refinement for Phase 32 (API scopes).

### V5.0 New Authorization Requirements

| Phase | New Guard Needed | Purpose |
|---|---|---|
| 28 (Knowledge Graph) | None — uses `verify_workspace_access` | Edge CRUD within workspace |
| 32 (Open API) | `verify_api_key`, `verify_oauth_token`, `check_api_scope` | External API consumers |
| 34 (Verification) | `require_verifier_role` | Only authorized users can verify achievements |
| 35 (Passport) | `verify_passport_owner` | Only passport owner controls visibility |
| 36 (Org Intelligence) | `require_org_admin` | Org-level dashboards |
| 40 (Observatory) | `require_ecosystem_access` | Aggregated cross-org data |
| 41 (Federation) | `verify_federation_agreement` | Cross-org resource access |
| 44 (Governance) | `require_org_admin` + audit trail | Policy management |

---

## 4. Conclusion

The existing authorization framework is **well-applied** across all 40 routers. The dependency-injection pattern is clean and consistent. V5.0 will need 5-6 new guard functions to handle organization-level access, API consumers, verification roles, and federation agreements. These will follow the same `Depends()` pattern.
