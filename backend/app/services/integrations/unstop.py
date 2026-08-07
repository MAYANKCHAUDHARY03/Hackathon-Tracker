from typing import Dict, Any, List
import logging
from .base import SubmissionProviderAdapter, ExternalSubmissionData

logger = logging.getLogger(__name__)

class UnstopAdapter(SubmissionProviderAdapter):
    @property
    def provider_name(self) -> str:
        return "unstop"

    async def validate_credentials(self) -> bool:
        # Validate Unstop API key or client secret
        logger.info("Validating Unstop credentials...")
        token = self.credentials.get("api_key")
        return bool(token)

    async def fetch_submissions(self, hackathon_reference: str) -> List[ExternalSubmissionData]:
        # Implement actual Unstop API call here
        logger.info(f"Fetching submissions for Unstop hackathon {hackathon_reference}")
        return []

    async def fetch_submission_details(self, submission_id: str) -> ExternalSubmissionData:
        logger.info(f"Fetching Unstop submission details for {submission_id}")
        return ExternalSubmissionData(
            external_id=submission_id,
            status="unknown",
            title="Unknown Submission"
        )
