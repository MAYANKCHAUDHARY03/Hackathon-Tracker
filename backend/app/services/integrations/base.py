from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ExternalSubmissionData(BaseModel):
    external_id: str
    status: str
    title: str
    description: Optional[str] = None
    team_name: Optional[str] = None
    repository_url: Optional[str] = None
    demo_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SubmissionProviderAdapter(ABC):
    """
    Abstract base class for all external submission providers (e.g. Devfolio, Unstop, HackerEarth).
    """
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider"""
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate if the provided credentials are correct and active."""
        pass
        
    @abstractmethod
    async def fetch_submissions(self, hackathon_reference: str) -> List[ExternalSubmissionData]:
        """Fetch all submissions for a given hackathon from the provider."""
        pass
        
    @abstractmethod
    async def fetch_submission_details(self, submission_id: str) -> ExternalSubmissionData:
        """Fetch detailed information for a specific submission."""
        pass
        
    async def sync_submissions(self, hackathon_reference: str) -> List[ExternalSubmissionData]:
        """
        Safely fetch and return submissions, including basic audit logging.
        """
        logger.info(f"Starting sync from {self.provider_name} for event {hackathon_reference}")
        try:
            submissions = await self.fetch_submissions(hackathon_reference)
            logger.info(f"Successfully fetched {len(submissions)} submissions from {self.provider_name}")
            return submissions
        except Exception as e:
            logger.error(f"Failed to sync submissions from {self.provider_name}: {str(e)}")
            raise
