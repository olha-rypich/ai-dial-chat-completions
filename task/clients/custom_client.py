import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role

class CustomDialClient(BaseClient):
  def __init__(self, deployment_name: str, api_key: str):
    super().__init__(deployment_name, api_key)
    self._endpoint = f"{DIAL_ENDPOINT}/openai/deployments/{deployment_name}/chat/completions"

  def get_completion(self, messages: list[Message]) -> Message:
    headers = {
      "api-key": self._api_key,
      "Content-Type": "application/json"
    }
    payload = {
      "messages": [m.to_dict() for m in messages]
    }

    resp = requests.post(self._endpoint, headers=headers, json=payload)

    if resp.status_code == 200:
      resp_json = resp.json()
      choices = resp_json.get("choices", [])

      if choices:
        content = choices[0].get("message", {}).get("content", "")
        print(content)
        return Message(Role.AI, content)
      raise Exception("No choices found in response")
    else:
      raise Exception(f"HTTP {resp.status_code}: {resp.text}")

  async def stream_completion(self, messages: list[Message]) -> Message:
    headers = {
      "api-key": self._api_key,
      "Content-Type": "application/json"
    }
    payload = {
      "stream": True,
      "messages": [m.to_dict() for m in messages]
    }
    content_parts = []

    async with aiohttp.ClientSession() as session:
      async with session.post(self._endpoint, headers=headers, json=payload) as resp:
        if resp.status == 200:
          async for raw_line in resp.content:
            line = raw_line.decode('utf-8').strip()

            if line.startswith("data: "):
              chunk = line[6:].strip()

              if chunk != "[DONE]":
                snippet = self._get_content_snippet(chunk)
                print(snippet, end='', flush=True)
                content_parts.append(snippet)
              else:
                print()
        else:
          error_msg = await resp.text()
          print(f"{resp.status} {error_msg}")
        return Message(Role.AI, ''.join(content_parts))

  def _get_content_snippet(self, data: str) -> str:
    """
    Extracts the content snippet from a streaming data chunk.
    """
    try:
      parsed = json.loads(data)
      choices = parsed.get("choices", [])

      if choices:
        delta = choices[0].get("delta", {})
        return delta.get("content", "")
    except Exception as e:
      print(f"Error parsing chunk: {e}")
    return ""
