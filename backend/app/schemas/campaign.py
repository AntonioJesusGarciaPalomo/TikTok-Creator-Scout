from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Campaign Schemas
class CampaignBase(BaseModel):
    name: str
    description: str
    target_segment: Optional[str] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    auto_send: bool = False
    daily_limit: int = Field(default=50, ge=1, le=500)
    messages_per_hour: int = Field(default=10, ge=1, le=100)

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_segment: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    auto_send: Optional[bool] = None
    daily_limit: Optional[int] = None
    messages_per_hour: Optional[int] = None
    is_active: Optional[bool] = None

class CampaignResponse(CampaignBase):
    id: int
    is_active: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_targets: int
    messages_sent: int
    messages_failed: int
    responses_received: int
    response_rate: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CampaignWithStats(CampaignResponse):
    pending_messages: int
    queued_messages: int

# Creator Search Schemas
class CreatorSearchBase(BaseModel):
    search_type: str = Field(..., description="Type: hashtag, keyword, trending, music, location")
    query: str = Field(..., description="Search query (hashtag, keyword, music_id, etc.)")
    location: Optional[str] = None
    category: Optional[str] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class CreatorSearchCreate(CreatorSearchBase):
    campaign_id: Optional[int] = None

class CreatorSearchResponse(CreatorSearchBase):
    id: int
    campaign_id: Optional[int] = None
    results_count: int
    last_executed: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Search Execution
class ExecuteSearchRequest(BaseModel):
    search_type: str = Field(..., description="hashtag, keyword, trending, music")
    query: str
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    auto_scrape: bool = Field(default=True, description="Automatically scrape discovered creators")
    save_search: bool = Field(default=True, description="Save search to database")

class BulkSearchRequest(BaseModel):
    searches: List[Dict[str, Any]] = Field(
        ...,
        description="List of searches: [{'type': 'hashtag', 'query': 'fitness', 'filters': {...}}, ...]"
    )
    auto_scrape: bool = True
    deduplicate: bool = True

class SearchResultsResponse(BaseModel):
    search_type: str
    query: str
    total_found: int
    creators: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]

class BulkSearchResponse(BaseModel):
    total_searches: int
    total_creators_found: int
    unique_creators: int
    results_by_search: Dict[str, SearchResultsResponse]
