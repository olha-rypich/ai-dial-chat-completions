import asyncio
import os

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

async def start(stream_mode: bool) -> None:
  api_key = os.getenv("DIAL_API_KEY")

  if not api_key:
    raise EnvironmentError("DIAL_API_KEY environment variable is not set.")

  dial_client = DialClient(deployment_name="gpt-4o", api_key=api_key)
  custom_dial_client = CustomDialClient(deployment_name="gpt-4o", api_key=api_key)

  conversation = Conversation()

  print("Enter a system prompt or press Enter to use the default.")

  sys_prompt = input("System prompt: ").strip()

  if sys_prompt:
      conversation.add_message(Message(Role.SYSTEM, sys_prompt))
      print("System prompt added successfully.")
  else:
    conversation.add_message(Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT))
    print(f"Default system prompt applied: '{DEFAULT_SYSTEM_PROMPT}'")

  print("\nType your message or 'exit' to leave the chat.")

  while True:
    user_input = input("User: ").strip()

    if user_input.lower() == "exit":
      print("Chat ended.")
      break

    conversation.add_message(Message(Role.USER, user_input))

    print("Assistant:")

    if stream_mode:
      response_msg = await dial_client.stream_completion(conversation.get_messages())
    else:
      response_msg = dial_client.get_completion(conversation.get_messages())

    conversation.add_message(response_msg)

    print(response_msg.content)

    print("\n[Debug] CustomDialClient response:")

    if stream_mode:
      debug_response = await custom_dial_client.stream_completion(conversation.get_messages())
    else:
      debug_response = custom_dial_client.get_completion(conversation.get_messages())
    
    print(debug_response.content)
    print()

if __name__ == "__main__":
  asyncio.run(start(True))
