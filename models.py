from pydantic import BaseModel
from typing import List, Literal


class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str
    location: str


class Experience(BaseModel):
    title: str
    company: str
    duration: str
    description: str


class Education(BaseModel):
    degree: str
    institution: str
    year: str
    description: str


class Language(BaseModel):
    language: str
    proficiency: str


class CVData(BaseModel):
    personalInfo: PersonalInfo
    summary: str
    experience: List[Experience]
    education: List[Education]
    skills: List[str]
    languages: List[Language]


class PersonalizationData(BaseModel):
    motivation: str  # Why do you want to work here?
    highlightExperience: str  # Which experience should be emphasized?
    passionValues: str  # What do you care about professionally?


class GenerationSettings(BaseModel):
    tone: Literal["formal", "friendly", "enthusiastic", "straightforward", "creative", "assertive"]
    length: Literal["short", "standard", "long"]
    language: Literal["english", "polish", "german", "french", "spanish", "italian", "dutch", "portuguese"]
    careerChange: bool
    roleLevel: Literal["entry-level", "mid-level", "senior", "executive"]


class CoverLetterRequest(BaseModel):
    cvData: CVData
    personalizationData: PersonalizationData
    generationSettings: GenerationSettings
    jobDescription: str


class CoverLetterResponse(BaseModel):
    coverLetter: str
    success: bool
    message: str = "" 