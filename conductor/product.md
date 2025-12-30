# Product Guide: AI-Powered SWOT Analysis Agent

## 1. Initial Concept

This project will create an Agent Development Kit (ADK) agent that performs a comprehensive SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis on a given company. The agent will leverage the built-in `google_search` tool to gather information. The final analysis will be delivered in two formats: a well-formatted message in the chat window and a branded PDF document. The generated PDF will be stored in a Google Cloud Storage (GCS) bucket in a `pdfs/` folder, and a link to the file will be provided to the user.

## 2. Target Audience

The primary users for this agent are **business analysts** who require quick, automated, and reliable company research to support their strategic planning and decision-making processes.

## 3. Core Features & Functionality

*   **SWOT Analysis:** The agent's primary function is to conduct a SWOT analysis on any company provided by the user.
*   **PDF Generation:** The agent will generate a professional, branded PDF of the SWOT analysis. The PDF will support custom headers and footers to align with corporate branding.
*   **Dual-Language Support:** All output, including the chat response and the PDF content, will be available in both **English** and **Italian**.
*   **GCS Integration:** Generated PDFs will be automatically uploaded to a designated GCS bucket, and a direct access link will be returned to the user.
*   **Data Grounding:** The agent will use the `google_search` tool to ensure the analysis is based on up-to-date, publicly available information.

## 4. User Interaction

Users will interact with the agent through the standard **ADK Web** interface. No custom user interface is required. The user will simply provide the company name in the chat to initiate the SWOT analysis.

