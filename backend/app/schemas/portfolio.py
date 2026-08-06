from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PortfolioItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str # 'team', 'project', etc
    url: Optional[str]
    date: datetime

class UserPortfolio(BaseModel):
    user_id: str
    full_name: str
    bio: Optional[str]
    items: List[PortfolioItem]
