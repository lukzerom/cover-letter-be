# Cover Letter Generator API

A simple Python API built with FastAPI for parsing CVs and generating personalized cover letters using OpenAI.

## Features

- **CV Parsing**: Upload PDF CVs and extract structured data (personal info, experience, education, skills, etc.)
- **Cover Letter Generation**: Generate personalized cover letters based on CV data, job descriptions, and user preferences
- **OpenAI Integration**: Uses GPT-3.5-turbo for intelligent CV parsing and cover letter writing
- **CORS Support**: Ready for frontend integration

## Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the server**:

   ```bash
   python main.py
   ```

   Or with uvicorn:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### 1. Parse CV

- **POST** `/parse-cv`
- **Description**: Upload a PDF CV and get structured data
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: PDF file (required)
- **Response**: CVData object with parsed information

### 2. Generate Cover Letter

- **POST** `/generate-cover-letter`
- **Description**: Generate a personalized cover letter
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "cvData": {
      /* CVData object */
    },
    "personalizationData": {
      "motivation": "Why you want to work there",
      "highlightExperience": "Experience to emphasize",
      "passionValues": "Professional values"
    },
    "generationSettings": {
      "tone": "formal|friendly|enthusiastic|straightforward|creative|assertive",
      "length": "short|standard|long",
      "language": "english|polish|german|french|spanish|italian|dutch|portuguese",
      "careerChange": false,
      "roleLevel": "entry-level|mid-level|senior|executive"
    },
    "jobDescription": "Full job posting text"
  }
  ```
- **Response**: CoverLetterResponse with generated text

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Example

1. **Parse CV**:

   ```bash
   curl -X POST "http://localhost:8000/parse-cv" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@your_cv.pdf"
   ```

2. **Generate Cover Letter**:
   ```bash
   curl -X POST "http://localhost:8000/generate-cover-letter" \
        -H "accept: application/json" \
        -H "Content-Type: application/json" \
        -d @cover_letter_request.json
   ```

## Development

The API is built with:

- **FastAPI**: Modern, fast web framework
- **OpenAI**: GPT-3.5-turbo for AI processing
- **PyPDF2**: PDF text extraction
- **Pydantic**: Data validation and serialization

## Error Handling

The API includes proper error handling for:

- Invalid file formats (only PDF supported)
- OpenAI API errors
- JSON parsing errors
- File processing errors

All errors return appropriate HTTP status codes and descriptive messages.
