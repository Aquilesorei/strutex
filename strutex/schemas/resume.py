"""
Resume/CV schema for structured extraction.

Covers professional resumes and curriculum vitae.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """A work experience entry."""
    company: str = Field(..., description="Company/employer name")
    title: str = Field(..., description="Job title/position")
    location: Optional[str] = Field(None, description="Work location")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date (or 'Present')")
    is_current: bool = Field(False, description="Whether this is the current position")
    description: Optional[str] = Field(None, description="Role description")
    achievements: List[str] = Field(
        default_factory=list,
        description="Key achievements/responsibilities"
    )


class Education(BaseModel):
    """An education entry."""
    institution: str = Field(..., description="School/university name")
    degree: Optional[str] = Field(None, description="Degree type (BS, MS, PhD, etc.)")
    field_of_study: Optional[str] = Field(None, description="Major/field of study")
    location: Optional[str] = Field(None, description="Institution location")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End/graduation date")
    gpa: Optional[str] = Field(None, description="GPA if listed")
    honors: Optional[str] = Field(None, description="Honors, awards, or distinctions")


class Certification(BaseModel):
    """A certification or license."""
    name: str = Field(..., description="Certification name")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    date: Optional[str] = Field(None, description="Date obtained")
    expiry: Optional[str] = Field(None, description="Expiration date if applicable")
    credential_id: Optional[str] = Field(None, description="Credential ID/number")


class Resume(BaseModel):
    """
    Professional resume/CV schema.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.schemas import RESUME
        >>> 
        >>> processor = DocumentProcessor()
        >>> resume = processor.process("resume.pdf", "Extract resume", model=RESUME)
        >>> print(f"{resume.name}: {len(resume.work_experience)} positions")
    """
    
    # Personal info
    name: str = Field(..., description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State or location")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL or username")
    github: Optional[str] = Field(None, description="GitHub URL or username")
    website: Optional[str] = Field(None, description="Personal website/portfolio")
    
    # Summary
    summary: Optional[str] = Field(None, description="Professional summary/objective")
    
    # Skills
    skills: List[str] = Field(
        default_factory=list,
        description="Technical and professional skills"
    )
    
    # Experience
    work_experience: List[WorkExperience] = Field(
        default_factory=list,
        description="Work experience entries"
    )
    
    # Education
    education: List[Education] = Field(
        default_factory=list,
        description="Education entries"
    )
    
    # Certifications
    certifications: List[Certification] = Field(
        default_factory=list,
        description="Certifications and licenses"
    )
    
    # Additional
    languages: List[str] = Field(
        default_factory=list,
        description="Languages spoken"
    )
    
    interests: List[str] = Field(
        default_factory=list,
        description="Interests/hobbies if listed"
    )
    
    publications: List[str] = Field(
        default_factory=list,
        description="Publications if listed"
    )


# Convenient schema instance
RESUME = Resume
