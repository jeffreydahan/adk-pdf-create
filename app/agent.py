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

import base64
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models import Gemini
from app.tools import fetch_pdf_from_url, generate_pdf_report
import os
import google.auth
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types


_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def embed_pdf_in_response(
    callback_context: CallbackContext,
) -> genai_types.Content | None:
    """Checks for a Base64 encoded PDF in state, decodes it, and embeds it in the final response."""
    if pdf_base64 := callback_context.state.get("pdf_base64"):
        # Clear the data from state to avoid re-sending
        callback_context.state["pdf_base64"] = None
        # Decode the Base64 string back to bytes
        pdf_bytes = base64.b64decode(pdf_base64)
        # Construct the structured response for the UI
        return genai_types.Content(
            parts=[
                genai_types.Part(
                    inline_data=genai_types.Blob(
                        mime_type="application/pdf", data=pdf_bytes
                    )
                )
            ]
        )
    return None


root_agent = Agent(
    name="pdf_loader_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""
    Your job is to help users get a PDF file, either by fetching it from a URL or by generating a new one on a given topic.

    - First, ask the user for the URL of the PDF or the topic for the report.
    - Then, use the appropriate tool (`fetch_pdf_from_url` or `generate_pdf_report`).
    - After the tool succeeds, your final response should be a simple confirmation message, like "Here is the PDF you requested." or "I've generated the report for you."

    If the user asks to use the default PDF, use the following URL:
    'https://services.google.com/fh/files/misc/professional_cloud_architect_renewal_exam_guide_eng.pdf'
    """,
    tools=[fetch_pdf_from_url, generate_pdf_report],
    after_agent_callback=embed_pdf_in_response,
)

app = App(root_agent=root_agent, name="app")
