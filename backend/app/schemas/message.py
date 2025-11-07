from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from ..models.message import MessageStatus

# Message Template Schemas
class MessageTemplateBase(BaseModel):
    name: str
    segment: str
    subject: str
    template_text: str
    is_active: bool = True

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    segment: Optional[str] = None
    subject: Optional[str] = None
    template_text: Optional[str] = None
    is_active: Optional[bool] = None

class MessageTemplateResponse(MessageTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Message Schemas
class MessageBase(BaseModel):
    creator_id: int
    campaign_id: Optional[int] = None
    template_id: Optional[int] = None
    subject: Optional[str] = None
    content: str
    scheduled_at: Optional[datetime] = None

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[MessageStatus] = None
    scheduled_at: Optional[datetime] = None
    response_text: Optional[str] = None

class MessageResponse(MessageBase):
    id: int
    status: MessageStatus
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    response_text: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageWithCreator(MessageResponse):
    creator_username: Optional[str] = None
    creator_display_name: Optional[str] = None

# Message Generation Request
class GenerateMessageRequest(BaseModel):
    creator_id: int
    template_id: Optional[int] = None
    use_ai: bool = True
    tone: str = Field(default="professional", description="Tone: professional, casual, friendly")
    language: str = Field(default="es", description="Language code: es, en, etc.")

class BulkGenerateMessagesRequest(BaseModel):
    creator_ids: List[int]
    campaign_id: Optional[int] = None
    use_ai: bool = True
    tone: str = "professional"
    language: str = "es"

class GenerateMessageResponse(BaseModel):
    message_id: int
    creator_id: int
    content: str
    status: str

# Message Sending
class SendMessageRequest(BaseModel):
    message_id: int

class SendBatchMessagesRequest(BaseModel):
    message_ids: List[int]
    delay_between_messages: float = Field(default=5.0, ge=1.0, le=60.0)

class SendMessageResponse(BaseModel):
    message_id: int
    success: bool
    error: Optional[str] = None

class BatchSendResponse(BaseModel):
    total: int
    success: List[int]
    failed: List[int]
    skipped: List[int]

class SendingStatsResponse(BaseModel):
    total_sent: int
    total_failed: int
    total_queued: int
    total_responded: int
    response_rate: float
    rate_limits: dict
