from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role

class DialClient(BaseClient):
  def __init__(self, deployment_name: str, api_key: str):
    super().__init__(deployment_name, api_key)

    self.dial_sync = Dial(
      base_url=DIAL_ENDPOINT,
      api_key=self._api_key,
    )
    self.dial_async = AsyncDial(
      base_url=DIAL_ENDPOINT,
      api_key=self._api_key,
    )

  def get_completion(self, messages: list[Message]) -> Message:
    payload = [m.to_dict() for m in messages]
    result = self.dial_sync.chat.completions.create(
      deployment_name=self._deployment_name,
      stream=False,
      messages=payload,
    )

    if result.choices:
      first_choice = result.choices[0]
      
      if first_choice.message:
        print(first_choice.message.content)

        return Message(Role.AI, first_choice.message.content)
    raise Exception("No choices in response found")

  async def stream_completion(self, messages: list[Message]) -> Message:
    payload = [m.to_dict() for m in messages]

    stream = await self.dial_async.chat.completions.create(
      deployment_name=self._deployment_name,
      messages=payload,
      stream=True,
    )

    content_chunks = []

    async for part in stream:
      if part.choices and len(part.choices) > 0:
        delta = part.choices[0].delta

        if delta and delta.content:
          print(delta.content, end='', flush=True)
          content_chunks.append(delta.content)

    print()

    return Message(Role.AI, ''.join(content_chunks))
