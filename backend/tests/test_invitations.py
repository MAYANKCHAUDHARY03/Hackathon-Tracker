import pytest
from httpx import AsyncClient


# ── Helpers ──────────────────────────────────────────────────────────────────

async def register_user(client: AsyncClient, email: str, name: str) -> dict:
    """Register a user and return {token, headers, workspaces}."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": name, "password": "password123"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    ws_resp = await client.get("/api/v1/workspaces", headers=headers)
    assert ws_resp.status_code == 200

    return {
        "token": token,
        "headers": headers,
        "workspaces": ws_resp.json(),
    }


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_invitation(async_client: AsyncClient):
    """Owner can invite a new user by email."""
    owner = await register_user(async_client, "owner1@test.com", "Owner One")
    ws_id = owner["workspaces"][0]["id"]

    resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "invitee1@test.com", "role": "member"},
        headers=owner["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "invitee1@test.com"
    assert data["workspace_role"] == "member"
    assert data["status"] == "pending"
    assert "token_hash" in data


@pytest.mark.asyncio
async def test_list_pending_invitations(async_client: AsyncClient):
    """Owner can list pending invitations for a workspace."""
    owner = await register_user(async_client, "owner2@test.com", "Owner Two")
    ws_id = owner["workspaces"][0]["id"]

    # Create two invitations
    await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "a@test.com", "role": "member"},
        headers=owner["headers"],
    )
    await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "b@test.com", "role": "admin"},
        headers=owner["headers"],
    )

    resp = await async_client.get(
        f"/api/v1/workspaces/{ws_id}/invitations",
        headers=owner["headers"],
    )
    assert resp.status_code == 200
    invitations = resp.json()
    assert len(invitations) == 2
    emails = {inv["email"] for inv in invitations}
    assert emails == {"a@test.com", "b@test.com"}


@pytest.mark.asyncio
async def test_duplicate_invitation_rejected(async_client: AsyncClient):
    """Cannot send two pending invitations to the same email."""
    owner = await register_user(async_client, "owner3@test.com", "Owner Three")
    ws_id = owner["workspaces"][0]["id"]

    resp1 = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "dup@test.com", "role": "member"},
        headers=owner["headers"],
    )
    assert resp1.status_code == 200

    resp2 = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "dup@test.com", "role": "admin"},
        headers=owner["headers"],
    )
    assert resp2.status_code == 400
    assert "already sent" in resp2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_revoke_invitation(async_client: AsyncClient):
    """Owner can revoke a pending invitation."""
    owner = await register_user(async_client, "owner4@test.com", "Owner Four")
    ws_id = owner["workspaces"][0]["id"]

    create_resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "revokee@test.com", "role": "member"},
        headers=owner["headers"],
    )
    inv_id = create_resp.json()["id"]

    revoke_resp = await async_client.delete(
        f"/api/v1/invitations/{inv_id}",
        headers=owner["headers"],
    )
    assert revoke_resp.status_code == 204

    # Verify it no longer appears in the list
    list_resp = await async_client.get(
        f"/api/v1/workspaces/{ws_id}/invitations",
        headers=owner["headers"],
    )
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_accept_invitation(async_client: AsyncClient):
    """Invited user can accept and join the workspace."""
    owner = await register_user(async_client, "owner5@test.com", "Owner Five")
    ws_id = owner["workspaces"][0]["id"]

    # Owner invites invitee
    create_resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "joiner@test.com", "role": "member"},
        headers=owner["headers"],
    )
    token_hash = create_resp.json()["token_hash"]

    # Register the invitee
    invitee = await register_user(async_client, "joiner@test.com", "Joiner")

    # Accept invitation
    accept_resp = await async_client.post(
        f"/api/v1/invitations/{token_hash}/accept",
        json={},
        headers=invitee["headers"],
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    # Invitee should now have 2 workspaces (personal + owner's)
    ws_resp = await async_client.get("/api/v1/workspaces", headers=invitee["headers"])
    assert ws_resp.status_code == 200
    assert len(ws_resp.json()) == 2


@pytest.mark.asyncio
async def test_accept_invitation_wrong_email(async_client: AsyncClient):
    """Cannot accept an invitation addressed to a different email."""
    owner = await register_user(async_client, "owner6@test.com", "Owner Six")
    ws_id = owner["workspaces"][0]["id"]

    create_resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "right@test.com", "role": "member"},
        headers=owner["headers"],
    )
    token_hash = create_resp.json()["token_hash"]

    # Register someone with a different email
    wrong_user = await register_user(async_client, "wrong@test.com", "Wrong User")

    accept_resp = await async_client.post(
        f"/api/v1/invitations/{token_hash}/accept",
        json={},
        headers=wrong_user["headers"],
    )
    assert accept_resp.status_code == 400
    assert "different email" in accept_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_accept_invalid_token(async_client: AsyncClient):
    """Accepting with a bogus token returns 404."""
    user = await register_user(async_client, "owner7@test.com", "Owner Seven")

    resp = await async_client.post(
        "/api/v1/invitations/totally-fake-token/accept",
        json={},
        headers=user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_invite_existing_member_rejected(async_client: AsyncClient):
    """Cannot invite someone who is already a workspace member."""
    owner = await register_user(async_client, "owner8@test.com", "Owner Eight")
    ws_id = owner["workspaces"][0]["id"]

    # Invite and accept first
    create_resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "member8@test.com", "role": "member"},
        headers=owner["headers"],
    )
    token_hash = create_resp.json()["token_hash"]

    invitee = await register_user(async_client, "member8@test.com", "Member Eight")
    await async_client.post(
        f"/api/v1/invitations/{token_hash}/accept",
        json={},
        headers=invitee["headers"],
    )

    # Try to invite same person again
    resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "member8@test.com", "role": "admin"},
        headers=owner["headers"],
    )
    assert resp.status_code == 400
    assert "already a member" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_admin_cannot_invite(async_client: AsyncClient):
    """A regular member cannot create invitations."""
    owner = await register_user(async_client, "owner9@test.com", "Owner Nine")
    ws_id = owner["workspaces"][0]["id"]

    # Invite a member
    create_resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "regular@test.com", "role": "member"},
        headers=owner["headers"],
    )
    token_hash = create_resp.json()["token_hash"]

    member = await register_user(async_client, "regular@test.com", "Regular")
    await async_client.post(
        f"/api/v1/invitations/{token_hash}/accept",
        json={},
        headers=member["headers"],
    )

    # Member tries to invite someone
    resp = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/invitations",
        json={"email": "another@test.com", "role": "member"},
        headers=member["headers"],
    )
    assert resp.status_code == 403
