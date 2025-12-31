# ruff: noqa
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models import Gemini
from google.adk.tools import google_search, ToolContext, AgentTool
from google.genai import types

import os
import google.auth
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import gcsfs
import uuid


_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def generate_and_upload_swot_pdf(swot_analysis_text: str, company_name: str, tool_context: ToolContext) -> str:
    """Generates a PDF document of the SWOT analysis and uploads it to GCS.

    Args:
        swot_analysis_text (str): The SWOT analysis content in Markdown format.
        company_name (str): The name of the company for which the SWOT analysis was performed.
        tool_context (ToolContext): The tool context object.

    Returns:
        str: The public URL of the uploaded PDF file.
    """
    # 1. Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom style for title
    title_style = ParagraphStyle('TitleStyle',
                                 parent=styles['h1'],
                                 alignment=TA_CENTER,
                                 spaceAfter=14)

    # Custom style for section headings
    heading_style = ParagraphStyle('HeadingStyle',
                                   parent=styles['h2'],
                                   spaceBefore=12,
                                   spaceAfter=6)

    story = []
    
    story.append(Paragraph(f"SWOT Analysis for {company_name}", title_style))
    story.append(Spacer(1, 0.2 * 0.4 * letter[1])) # Adjust spacing if needed


    # Basic parsing for Markdown headings and bullet points
    # This is a simple parser. For more complex Markdown, a dedicated parser would be needed.
    lines = swot_analysis_text.split('\n')
    current_section = ""
    for line in lines:
        if line.startswith('### '): # Markdown H3 for SWOT categories
            current_section = line[4:].strip()
            story.append(Paragraph(current_section, heading_style))
        elif line.startswith('* '): # Markdown bullet points
            story.append(Paragraph(f"• {line[2:].strip()}", styles['Normal']))
        elif line.strip(): # Regular text
            story.append(Paragraph(line.strip(), styles['Normal']))
    
    doc.build(story)
    pdf_content = buffer.getvalue()
    buffer.close()

    # 2. Upload to GCS
    fs = gcsfs.GCSFileSystem(project=project_id)
    bucket_name = "adk-pdf-create1"
    folder_name = "pdfs"
    file_name = f"SWOT_{company_name.replace(' ', '_')}_{uuid.uuid4()}.pdf"
    full_path = f"{bucket_name}/{folder_name}/{file_name}"

    try:
        with fs.open(full_path, 'wb') as f:
            f.write(pdf_content)
        
        # Constructing the public URL (assuming the bucket allows public access)
        public_url = f"https://storage.cloud.google.com/{full_path}"
        return public_url
    except Exception as e:
        tool_context.state['error'] = f"Failed to upload PDF to GCS: {e}"
        return f"Error uploading PDF: {e}"


pdf_generator_agent = Agent(
    name="pdf_generator_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a PDF Generator tool which also uploads PDFs to a
    Google Cloud Storage Bucket
    """,
    tools=[generate_and_upload_swot_pdf],
)


google_search_agent = Agent(
    name="google_search_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are a search agent. You use the 'google_search' tool to answer questions about general topics.",
    tools=[google_search],
)


root_agent = Agent(
    name="swot_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are a swot analysis agent that performs senior expert analysis. 
    
    1. ask the user for the company name to analyze
    2. perform the analysis using Google Search via the 'google_search_agent' 
    AgentTool
    3. present the analysis in nice markdown, including reference links
    4. ask the user if they want to generate a PDF
    5. if the user wants the PDF created, you will call the 
    pdf_generator_agent AgentTool to generate the PDF
    and upload it to GCS.
    6. let the user know this step succeeded and provide them the
    PDF url.  The url should always be structured like the following:
    https://storage.cloud.google.com/[bucket_name]/[folder_name]/[file_name]
    """,
    tools=[AgentTool(google_search_agent), AgentTool(pdf_generator_agent)],
)

app = App(root_agent=root_agent, name="app")
