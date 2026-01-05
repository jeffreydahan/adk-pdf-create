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
from app.tools import fetch_pdf_from_url, generate_pdf_report
import os
import google.auth


_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


root_agent = Agent(
    name="pdf_loader_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""
    Your job is to fetch a PDF from a given URL and return it to the user to be displayed in the UI.
    You can also generate a PDF report on a given topic.
    Ask the user for the URL of the PDF or the topic for the report.

    If the user asks to use the default PDF, use the following URL:
    'https://services.google.com/fh/files/misc/professional_cloud_architect_renewal_exam_guide_eng.pdf'
    """,
    tools=[fetch_pdf_from_url, generate_pdf_report],
)

app = App(root_agent=root_agent, name="app")
