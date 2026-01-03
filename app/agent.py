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
from app.tools import load_pdf_from_url, get_saved_artifact
import os
import google.auth


_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


root_agent = Agent(
    name="artifact_loader_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="Your job is to call the `load_pdf_from_url` tool with the url 'https://services.google.com/fh/files/misc/professional_cloud_architect_renewal_exam_guide_eng.pdf', and then call the `get_saved_artifact` tool with the filename 'professional_cloud_architect_renewal_exam_guide_eng.pdf'.",
    tools=[load_pdf_from_url, get_saved_artifact],
)

app = App(root_agent=root_agent, name="app")
