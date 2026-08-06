# Stage 4: SCIM User Provisioning

## Implementation Summary
- **ScimToken Model**: Created a database model (`ScimToken`) with `token_hash` that maps directly to an `organization_id`. The plain text token is never stored.
- **SCIM Router**: Created `app/routers/scim.py` with standard SCIM 2.0 endpoints for `/Users`.
- **Organization-Scoped Auth**: Bearer tokens are validated against the `token_hash`. The derived `organization_id` strictly scopes all querying, listing, and provisioning. 
- **Provisioning Flow**: Users provisioned via POST `/Users` are created in the system with an unusable password (`!scim_provisioned`) and are automatically added as `member` to the target organization.
- **Update Flow**: PUT `/Users/{user_id}` supports updating basic user information (e.g. `active` status and `formatted` name).

Stage 4 complete. Proceeding to External Calendars.
