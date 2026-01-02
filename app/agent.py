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
from google.adk.tools import google_search, AgentTool
from google.genai import types

import os
import google.auth


_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


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
    """,
    tools=[AgentTool(google_search_agent),],
)

app = App(root_agent=root_agent, name="app")
