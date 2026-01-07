# ruff: noqa
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 20 (the "License");
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

import base64
import io
from google.adk.tools import tool_context as tool_context_module
from google.genai import types
# You'll need a library to generate PDFs, e.g., ReportLab
from reportlab.pdfgen import canvas
import httpx
from google.adk.tools import tool_context as tool_context_module
from google.genai import types
import urllib.request
import os
import logging
from google.cloud import logging as gcp_logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Google Cloud Logging
cloud_logger = None
gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

if gcp_project_id:
    try:
        log_client = gcp_logging.Client(project=gcp_project_id)
        gcp_handler = log_client.get_default_handler()
        cloud_logger = logging.getLogger("cloud")
        cloud_logger.addHandler(gcp_handler)
        cloud_logger.setLevel(logging.INFO)
        logger.info(f"Google Cloud Logging initialized for project: {gcp_project_id}")
    except Exception as e:
        logger.error(f"Failed to set up Google Cloud Logging for project {gcp_project_id}: {e}")
else:
    logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set. Google Cloud Logging will not be active.")


def log_info(message):
    logger.info(message)
    if cloud_logger:
        cloud_logger.info(message)


async def generate_pdf_report(
    tool_context: tool_context_module.ToolContext, topic: str
) -> dict:
    """
    Generates a PDF document about the given topic and returns it to the user.
    """
    log_info(f"Received request to generate PDF report for topic: {topic}")
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)

        # Add content to the PDF
        c.drawString(100, 750, f"Report on: {topic}")
        c.drawString(100, 730, "This is the content of the PDF.")
        # ... Add more complex content as needed ...
        c.save()
        log_info("PDF content created in-memory.")

        pdf_bytes = buffer.getvalue()
        buffer.close()
        log_info(f"PDF bytes generated. Size: {len(pdf_bytes)} bytes.")

        # Base64 encode the bytes to store in the JSON-serializable state
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        tool_context.state["pdf_base64"] = pdf_base64
        log_info("PDF has been Base64 encoded and saved to session state.")

        return {
            "status": "success",
            "message": f"I have generated the PDF report on '{topic}'.",
        }

    except Exception as e:
        log_info(f"Failed to generate PDF for topic {topic}: {e}")
        logging.exception(f"Detailed error during PDF generation for {topic}: {e}")
        return {
            "status": "error",
            "message": f"Sorry, I encountered an error while generating the PDF for '{topic}'.",
        }


async def fetch_pdf_from_url(
    tool_context: tool_context_module.ToolContext, url: str
) -> dict:
    """
    Fetches a PDF from a public URL and returns it to the user.

    Args:
        url: The public URL of the PDF file.
    """
    log_info(f"Tool context set for fetch_pdf_from_url with URL: {url}")
    if not url.lower().endswith(".pdf"):
        log_info(f"URL does not end with .pdf: {url}")
        return {"error": "The provided URL does not appear to be a PDF."}

    try:
        log_info(f"Starting PDF download from URL: {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            file_bytes = response.content
            log_info(
                f"Successfully downloaded PDF from URL: {url}. Size: {len(file_bytes)} bytes."
            )
            mime_type = response.headers.get("Content-Type", "application/pdf")

            if "application/pdf" not in mime_type:
                log_info(
                    f"The content at the URL is not a PDF. MIME type found: {mime_type}"
                )
                return {
                    "error": f"The content at the URL is not a PDF. MIME type found: {mime_type}"
                }

            # Base64 encode the bytes to store in the JSON-serializable state
            pdf_base64 = base64.b64encode(file_bytes).decode("utf-8")
            tool_context.state["pdf_base64"] = pdf_base64
            log_info("PDF has been Base64 encoded and saved to session state.")

            file_name = os.path.basename(url) or "downloaded.pdf"

            return {
                "status": "success",
                "detail": f"Successfully fetched '{file_name}'.",
            }

    except httpx.RequestError as e:
        log_info(f"Error fetching PDF from {url}: {e}")
        return {"error": f"Network error while fetching PDF: {str(e)}"}
    except Exception as e:
        log_info(f"An unexpected error occurred: {e}")
        logging.exception(f"Detailed error during PDF fetch for {url}: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}
