from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class Contact(BaseModel):
    name: str
    title: str
    email: Optional[EmailStr] = None
    linkedin: Optional[str] = None
    confidence: Optional[float] = None

class Signals(BaseModel):
    recent_hiring: Optional[bool] = None
    new_funding: Optional[bool] = None
    funding_amount: Optional[float] = None
    funding_round: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    hiring_roles: Optional[List[str]] = None

class Company(BaseModel):
    company_name: str
    domain: str
    revenue: Optional[float] = None
    industry: str
    employee_count: Optional[int] = None
    location: Optional[str] = None
    funding_stage: Optional[str] = None
    contacts: List[Contact] = []
    signals: Signals = Signals()
    source: List[str] = []
    confidence: float = 0.0

class ICP(BaseModel):
    revenue_min: Optional[float] = None
    revenue_max: Optional[float] = None
    industry: List[str] = []
    geography: List[str] = []
    employee_count_min: Optional[int] = None
    employee_count_max: Optional[int] = None
    keywords: List[str] = []
    signals: Dict[str, Any] = {}