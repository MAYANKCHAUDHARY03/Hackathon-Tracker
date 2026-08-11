# Privacy Audit — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: PII fields, data minimization, privacy implications of Knowledge Graph  
**Purpose**: Ensure privacy compliance before expanding the data model

---

## 1. PII Field Inventory

### Direct PII (Personally Identifiable Information)

| Model | Field | PII Type | Exposed in API? |
|---|---|---|---|
| User | `email` | Contact | Yes (profile) |
| User | `password_hash` | Credential | Never |
| User | `full_name` | Identity | Yes (profile) |
| User | `avatar_url` | Identity | Yes (profile) |
| User | `github_handle` | Identity | Yes (profile) |
| User | `linkedin_url` | Identity | Yes (profile) |
| Person | `email` | Contact | Yes (admin only) |
| Person | `phone` | Contact | Yes (admin only) |
| Person | `full_name` | Identity | Yes (per visibility) |
| Person | `public_profile_url` | Identity | Yes |
| Person | `bio` | Personal | Yes |

### Indirect PII (contextually identifying)

| Model | Field | Risk |
|---|---|---|
| TeamMember | `user_id` + `team_id` | Links user to participation |
| Evaluation | `evaluator_person_id` | Identifies evaluator |
| Achievement | `user_id` | Links user to achievements |
| ActivityEvent | `actor_id` | Tracks user actions |
| AuditLog | `user_id` | Tracks user actions |
| Notification | `user_id` | User-specific |

---

## 2. Data Minimization Assessment

### API Response Analysis

| Endpoint Group | Minimization Status |
|---|---|
| Auth (`/auth/*`) | ✅ Returns token only, no PII in login response beyond user ID |
| Users (`/users/*`) | ⚠️ Returns full profile including all optional fields |
| Search (`/search`) | ✅ Returns entity summaries, not full records |
| Graph (`/graph/*`) | ⚠️ Node hydration returns full entity data |
| Evaluations | ✅ Evaluator name snapshot instead of full person data |

### Recommendations
1. **User profile endpoints**: Add field-level visibility controls (Phase 35 will address via Passport)
2. **Graph node hydration**: Return summary projection, not full entity. Strip PII fields from graph traversal responses.

---

## 3. Knowledge Graph Privacy Implications

### Risk: Relationship Inference
The Knowledge Graph creates edges like:
- `User → participated_in → Hackathon`
- `User → created_by → Project`
- `User → mentored_by → Person`

Even within a single workspace, this reveals **social graph** information:
- Who worked with whom
- What topics someone has expertise in
- Career trajectory across hackathons

### Mitigations (to implement in Phase 28)

1. **Visibility controls on edges**: Users can mark edges as `private` to exclude them from graph queries by other users.

2. **Permission-scoped traversal**: Graph traversal respects the caller's permission level:
   - Workspace admin: sees all edges in workspace
   - Workspace member: sees edges involving entities they have access to
   - Public/federated: sees only edges with `visibility=public`

3. **AI-inferred edges require consent**: If AI suggests a relationship involving a user, the user must approve it before it becomes visible.

4. **No cross-workspace graph leakage**: Graph traversal is always filtered by `workspace_id`. Phase 41 (Federation) will use `FederatedResource` references, not actual graph edges.

---

## 4. Data Retention Risks

| Data Category | Current Retention | Recommendation |
|---|---|---|
| User accounts | Indefinite | Phase 44 will add account deletion workflow |
| Activity events | Indefinite | Add retention policy (configurable per org) |
| Audit logs | Indefinite | Retain for compliance (min 1 year, configurable) |
| Graph edges | Indefinite | Auto-archive edges for soft-deleted entities |
| AI interaction logs | `AIPrivacyFilter` logs size only | ✅ No PII in AI logs |
| Notifications | Indefinite | Auto-expire after 90 days |

---

## 5. Third-Party Data Flows

| External Service | Data Sent | PII Included | Mitigation |
|---|---|---|---|
| Google Gemini API | Project data, search queries | Stripped by `AIPrivacyFilter` | ✅ |
| SAML/SSO Providers | Auth assertions | Email, name (standard SSO) | ✅ Required for SSO |
| Webhook deliveries | Event payloads | Depends on event type | ⚠️ Add PII filter to webhook payloads |

---

## 6. Conclusion

Privacy posture is **adequate for current scope**. The main gap is lack of user-controlled visibility on profile fields (addressed by Phase 35) and the need for data retention policies (addressed by Phase 44). The Knowledge Graph introduces relationship inference risks that will be mitigated by permission-scoped traversal and edge visibility controls in Phase 28.
