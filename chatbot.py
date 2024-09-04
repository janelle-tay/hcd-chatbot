import os
from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field
import openai
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY") or ""

# Default values for LLM clients
DEFAULT_CLIENT = "openai"
DEFAULT_MODEL_NAMES = {
    "openai": "gpt-4o-2024-08-06",
    "gemini": "models/gemini-1.5-flash"
}
TEMPERATURE = 0.0
MAX_TOKENS = 1024

# System Prompt
PROMPT = """
Insert prompt here
"""

class BaseChatMessage(BaseModel):
    attributes: Dict[str, Any] = Field(default_factory=dict)

class OpenAIChatMessage(BaseChatMessage):
    role: str
    content: str

class GeminiChatMessage(BaseChatMessage):
    role: str
    parts: str

ChatMessage = Union[OpenAIChatMessage, GeminiChatMessage]

class ConversationHistory(BaseModel):
    messages: List[ChatMessage]

class ConversationManager:
    def __init__(self, human_identifier: str, bot_identifier: str, system_identifier: str = None, message_class: ChatMessage = None):
        self.conversations = ConversationHistory(messages=[])
        self.human_identifier = human_identifier
        self.bot_identifier = bot_identifier
        self.system_identifier = system_identifier
        self.message_class = message_class

    def add_message(self, role: str, message: str):
        if self.message_class == OpenAIChatMessage:
            chat_message = self.message_class(role=role, content=message)
        elif self.message_class == GeminiChatMessage:
            chat_message = self.message_class(role=role, parts=message)
        else:
            raise ValueError(f"Unsupported message class: {self.message_class}")
        self.conversations.messages.append(chat_message)

    def add_human_message(self, message: str):
        self.add_message(self.human_identifier, message)

    def add_bot_message(self, message: str):
        self.add_message(self.bot_identifier, message)

    def add_system_message(self, message: str):
        self.add_message(self.system_identifier, message)

    def to_string(self, exclude_system_message: bool = True) -> str:
        conversation_history_string = ""
        for message in self.conversations.messages:
            role = message.role
            if isinstance(message, OpenAIChatMessage):
                content = message.content
            elif isinstance(message, GeminiChatMessage):
                content = message.parts
            else:
                raise ValueError(f"Unsupported message class: {type(message)}")

            if role == self.system_identifier:
                if not exclude_system_message:
                    conversation_history_string += f"{self.system_identifier}: {content}\n"
            elif role == self.human_identifier:
                conversation_history_string += f"{self.human_identifier}: {content}\n"
            else:
                conversation_history_string += f"{self.bot_identifier}: {content}\n"
        return conversation_history_string

    def get_conversation(self, exclude_system_message: bool = True) -> List[dict]:
        if exclude_system_message:
            return [message.dict() for message in self.conversations.messages if message.role != self.system_identifier]
        else:
            return [message.dict() for message in self.conversations.messages]
        
    def reset_conversation(self):
         #Re-initialise conversation object
        self.conversations = ConversationHistory(messages=[])

class RolePlayAgent:
    def __init__(self, human_identifier: str, bot_identifier: str, system_identifier: str = None, message_class: ChatMessage = None, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS, model_name: str = DEFAULT_MODEL_NAMES[DEFAULT_CLIENT]):
        self.human_identifier = human_identifier
        self.bot_identifier = bot_identifier
        self.system_identifier = system_identifier
        self.conversation_manager = ConversationManager(
            human_identifier=human_identifier,
            bot_identifier=bot_identifier,
            system_identifier=system_identifier,
            message_class=message_class,
        )
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_name = model_name

    def query(self, query: str) -> None:
        pass

    def save_chat_history(self, filename: str):
        # Saves the chat history to the user's Downloads folder
        try:
            # Locate the user's Downloads folder
            downloads_path = str(Path.home() / "Downloads")
            
            # Ensure filename ends with .txt
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            # Construct the full file path
            file_path = os.path.join(downloads_path, filename)
            
            # Save the chat history to the Downloads folder
            with open(file_path, 'w') as file:
                conversation = self.conversation_manager.to_string()
                file.write(conversation)
            print(f"\Chat history saved to {file_path}")
        except Exception as e:
            print(f"Failed to save conversation: {e}")

class OpenAIRolePlayAgent(RolePlayAgent):
    def __init__(self, system_prompt=PROMPT, human_identifier: str = "user", bot_identifier: str = "assistant", system_identifier: str = "system"):
        model_name = DEFAULT_MODEL_NAMES["openai"]
        super().__init__(human_identifier, bot_identifier, system_identifier, message_class=OpenAIChatMessage, model_name=model_name)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.system_prompt = system_prompt
        self.conversation_manager.add_system_message(self.system_prompt)

    def query(self, query: str) -> None:
        self.conversation_manager.add_human_message(query)
        messages = self.conversation_manager.get_conversation(exclude_system_message=False)
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[{"role": msg['role'], "content": msg['content']} for msg in messages],
                temperature=self.temperature,
                stream=True
            )
            text = []
            print("\n", end="")
            for part in response:
                if part.choices[0].delta.content is not None:
                    response_part = part.choices[0].delta.content
                    text.append(response_part)
            full_reply_content = "".join(text)
            self.conversation_manager.add_bot_message(full_reply_content)
        except Exception as e:
            print(f"An error occurred: {e}")
            
class GeminiRolePlayAgent(RolePlayAgent):
    def __init__(self, system_prompt=PROMPT, human_identifier: str = "user", bot_identifier: str = "model", system_identifier: str = "system"):
        model_name = DEFAULT_MODEL_NAMES["gemini"]
        super().__init__(human_identifier, bot_identifier, system_identifier, message_class=GeminiChatMessage, model_name=model_name)
        self.system_prompt = system_prompt
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            self.model_name,
            system_instruction=self.system_prompt,
        )

    def query(self, query: str) -> None:
        self.conversation_manager.add_human_message(query)
        raw_history = self.conversation_manager.get_conversation(exclude_system_message=False)
        history = [{k: v for k, v in item.items() if k != "attributes"} for item in raw_history]
        try:
            chat = self.model.start_chat(history=history)
            stream = chat.send_message(
                query,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                ),
            )
            text = []
            for part in stream:
                if part.text is not None:
                    response_part = part.text
                    text.append(response_part)
            full_reply_content = "".join(text).strip()
            self.conversation_manager.add_bot_message(full_reply_content)
        except Exception as e:
            print(f"An error occurred: {e}")


def instantiate_llm_model(client=DEFAULT_CLIENT) -> RolePlayAgent:
    if client == "openai":
        rpa = OpenAIRolePlayAgent()
    elif client == "gemini":
        rpa = GeminiRolePlayAgent()
    else:
        raise ValueError(f"Unsupported client: {client}")
    return rpa