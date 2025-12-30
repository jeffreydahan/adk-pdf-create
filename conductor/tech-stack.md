# Technology Stack

This document outlines the core technologies and platforms used for the AI-Powered SWOT Analysis Agent.

## 1. Core Development

*   **Programming Language:** Python
*   **Agent Framework:** Google Agent Development Kit (ADK)
*   **Web Framework:** FastAPI (for ADK's web interface and potential custom endpoints)

## 2. Cloud Infrastructure

*   **Cloud Platform:** Google Cloud Platform (GCP)
*   **Object Storage:** Google Cloud Storage (GCS) - specifically for storing generated PDF reports.

## 3. Key Services & Tools

*   **Search/Data Grounding:** Google Search (integrated via the ADK's built-in `google_search` tool for SWOT analysis data retrieval).
*   **PDF Generation:** A suitable Python library for PDF generation (e.g., ReportLab, WeasyPrint, or similar, to be determined during implementation).
*   **Deployment:** ADK's native deployment options on GCP, likely Cloud Run or Vertex AI Agent Engine.

## 4. Dual-Language Support

*   **Translation Services:** Python internationalization libraries (e.g., `gettext`) or integration with a translation API (e.g., Google Cloud Translation API) will be considered to support English and Italian outputs.
