import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import openai
from PyPDF2 import PdfReader
import io
from typing import Dict, Any

from models import CVData, CoverLetterRequest, CoverLetterResponse

# Load environment variables
load_dotenv()

app = FastAPI(title="Cover Letter Generator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")


def parse_cv_with_openai(cv_text: str) -> CVData:
    """Parse CV text using OpenAI to extract structured data."""
    try:
        prompt = f"""
        Please parse the following CV/Resume text and extract information into a JSON structure.
        Return ONLY valid JSON without any markdown formatting or additional text.
        
        The JSON should have this exact structure:
        {{
          "personalInfo": {{
            "name": "string",
            "email": "string", 
            "phone": "string",
            "location": "string"
          }},
          "summary": "string",
          "experience": [
            {{
              "title": "string",
              "company": "string", 
              "duration": "string",
              "description": "string"
            }}
          ],
          "education": [
            {{
              "degree": "string",
              "institution": "string",
              "year": "string", 
              "description": "string"
            }}
          ],
          "skills": ["string"],
          "languages": [
            {{
              "language": "string",
              "proficiency": "string"
            }}
          ]
        }}
        
        If any information is missing, use empty strings or empty arrays as appropriate.
        
        CV Text:
        {cv_text}
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a CV parsing assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        # Parse the JSON response
        json_str = response.choices[0].message.content.strip()
        # Remove potential markdown code blocks
        if json_str.startswith("```json"):
            json_str = json_str[7:-3]
        elif json_str.startswith("```"):
            json_str = json_str[3:-3]
            
        parsed_data = json.loads(json_str)
        return CVData(**parsed_data)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing OpenAI response as JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CV with OpenAI: {str(e)}")


def generate_cover_letter_with_openai(
    cv_data: CVData,
    personalization: dict,
    settings: dict,
    job_description: str
) -> str:
    """Generate cover letter using OpenAI."""
    try:
        # Convert tone and length to descriptive text
        tone_descriptions = {
            "formal": "professional and formal",
            "friendly": "warm and approachable",
            "enthusiastic": "energetic and passionate",
            "straightforward": "direct and concise",
            "creative": "creative and unique",
            "assertive": "confident and assertive"
        }
        
        length_descriptions = {
            "short": "Keep it concise (2-3 paragraphs, around 200-250 words)",
            "standard": "Standard length (3-4 paragraphs, around 300-400 words)",
            "long": "Detailed version (4-5 paragraphs, around 450-600 words)"
        }
        
        language_instructions = {
            "english": "Write the cover letter in English",
            "polish": "Write the cover letter in Polish (Polish language)",
            "german": "Write the cover letter in German (Deutsche Sprache)",
            "french": "Write the cover letter in French (Langue française)",
            "spanish": "Write the cover letter in Spanish (Idioma español)",
            "italian": "Write the cover letter in Italian (Lingua italiana)",
            "dutch": "Write the cover letter in Dutch (Nederlandse taal)",
            "portuguese": "Write the cover letter in Portuguese (Língua portuguesa)"
        }
        
        career_change_note = ""
        if settings["careerChange"]:
            career_change_note = "Note: This is a career change application, so emphasize transferable skills and motivation for the new field."
        
        prompt = f"""
        Write a cover letter based on the following information:
        
        **Applicant Information:**
        Name: {cv_data.personalInfo.name}
        Profile Summary (FOR CONTEXT ONLY - DO NOT copy or paraphrase directly): {cv_data.summary}
        
        **Key Experience:**
        {chr(10).join([f"- {exp.title} at {exp.company}: {exp.description}" for exp in cv_data.experience[:3]])}
        
        **Education:**
        {chr(10).join([f"- {edu.degree} from {edu.institution}" for edu in cv_data.education])}
        
        **Skills:** {', '.join(cv_data.skills[:10])}
        
        **Job Description:**
        {job_description}
        
        **Personalization:**
        - Motivation: {personalization["motivation"]}
        - Experience to highlight: {personalization["highlightExperience"]}
        - Professional values: {personalization["passionValues"]}
        
        **Requirements:**
        - Language: {language_instructions.get(settings["language"], f"Write the cover letter in {settings['language']}")}
        - Tone: {tone_descriptions.get(settings["tone"], settings["tone"])}
        - Length: {length_descriptions.get(settings["length"], settings["length"])}
        - Role level: {settings["roleLevel"]}
        {career_change_note}
        
        **CRITICAL INSTRUCTIONS:**
        - NEVER translate technical terms, programming languages, frameworks, tools, or job titles (e.g., keep "React", "Frontend Developer", "Python", "DevOps", "UI/UX", etc. in English)
        - Use the profile summary ONLY for understanding the candidate's background - generate fresh, original content for the cover letter
        - Do NOT copy or paraphrase the profile summary directly into the cover letter
        
        Create a compelling cover letter that:
        1. Opens with a strong hook related to the specific role
        2. Highlights relevant experience and skills from the CV (using original language, not copying the summary)
        3. Incorporates the personalization elements naturally
        4. Shows genuine interest in the company/role
        5. Ends with a confident call to action
        
        Format as a professional cover letter without date/address headers.
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an expert cover letter writer who can write in multiple languages. Write compelling, personalized cover letters that help candidates get interviews. Always write in the language specified in the user's requirements, but NEVER translate technical terms, programming languages, frameworks, tools, or job titles - keep them in English (e.g., React, Python, Frontend Developer, DevOps). Generate original content and do not copy or paraphrase profile summaries directly. Current language: {settings.get('language', 'english')}"},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.get("temperature", 0.7)
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Cover Letter Generator API", "version": "1.0.0"}


@app.post("/parse-cv", response_model=CVData)
async def parse_cv(file: UploadFile = File(...)):
    """
    Parse uploaded CV file and extract structured data.
    Supports PDF files.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        cv_text = extract_text_from_pdf(content)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Parse CV using OpenAI
        parsed_cv = parse_cv_with_openai(cv_text)
        
        return parsed_cv
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a personalized cover letter based on CV data, personalization, and job description.
    """
    try:
        cover_letter_text = generate_cover_letter_with_openai(
            cv_data=request.cvData,
            personalization=request.personalizationData.dict(),
            settings=request.generationSettings.dict(),
            job_description=request.jobDescription
        )
        
        return CoverLetterResponse(
            coverLetter=cover_letter_text,
            success=True,
            message="Cover letter generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return CoverLetterResponse(
            coverLetter="",
            success=False,
            message=f"Error generating cover letter: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 