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

from google.adk.tools import ToolContext
from google.genai import types
import urllib.request
import os


async def load_pdf_from_url(url: str, tool_context: ToolContext) -> str:
    """Loads a PDF from a URL and saves it as an artifact.

    Args:
        url (str): The URL to the PDF file.
        tool_context (ToolContext): The tool context object.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        with urllib.request.urlopen(url) as response:
            pdf_content = response.read()
    except Exception as e:
        return f"Error fetching PDF from URL: {e}"

    file_name = os.path.basename(url)

    try:
        await tool_context.save_artifact(
            file_name,
            #types.Part.from_data(data=pdf_content, mime_type="application/pdf"),
            types.Part(inline_data=types.Blob(mime_type="application/pdf", data=pdf_content)),
        )
        return f"Successfully loaded and saved '{file_name}' as an artifact."
    except Exception as e:
        tool_context.state['error'] = f"Failed to save PDF artifact: {e}"
        return f"Error saving PDF artifact: {e}"


async def get_saved_artifact(file_name: str, tool_context: ToolContext) -> dict:
    """Retrieves a saved artifact and confirms its existence.

    Args:
        file_name (str): The name of the artifact file to retrieve.
        tool_context (ToolContext): The tool context object.

    Returns:
        dict: A dictionary with the status of the operation and a message.
    """
    try:
        part = await tool_context.load_artifact(file_name)
        if part is None:
            return {"status": "error", "message": f"Artifact '{file_name}' not found."}
        return {"status": "success", "message": f"Artifact '{file_name}' retrieved successfully. It has {len(part.inline_data.data)} bytes and mime type {part.inline_data.mime_type}."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred while retrieving artifact {file_name}: {str(e)}"}
