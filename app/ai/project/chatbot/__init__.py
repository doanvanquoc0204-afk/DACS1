"""
Chatbot Module - AI Learning Management System

Module này chứa logic để tương tác với Gemini API.
Cung cấp interface cho chat và generation.

Tính năng nâng cao:
- Conversation Memory (summary-based cho long conversations)
- Streaming Response Support
- Conversation Persistence (save/load)
- Multiple Sessions Management
- Better Error Handling
"""

import os
import sys
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

# Thêm parent directory vào sys.path để import config
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import google.generativeai as genai
    from google.generativeai import GenerativeModel
    from google.api_core.exceptions import GoogleAPIError
except ImportError:
    raise ImportError(
        "google-generativeai chưa được cài đặt. "
        "Chạy: pip install google-generativeai"
    )

import config


# ============================================================
# Enums & Data Classes
# ============================================================

class MessageRole(Enum):
    """Enum cho message roles."""
    USER = "user"
    MODEL = "model"
    SYSTEM = "system"


@dataclass
class Message:
    """
    Dataclass cho một message trong conversation.

    Attributes:
        role: Vai trò của người gửi (user/model/system)
        content: Nội dung message
        timestamp: Thời gian tạo message
        metadata: Metadata bổ sung
    """
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert thành dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Tạo Message từ dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )


@dataclass
class Conversation:
    """
    Dataclass cho một conversation session.

    Attributes:
        id: Unique conversation ID
        title: Tiêu đề conversation (auto-generated hoặc custom)
        messages: Danh sách messages
        created_at: Thời gian tạo
        updated_at: Thời gian cập nhật cuối
        metadata: Metadata bổ sung
    """
    id: str
    title: str = "New Conversation"
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> Message:
        """Thêm message vào conversation."""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.updated_at = datetime.now().isoformat()
        return msg

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Convert messages thành format cho Gemini API."""
        return [
            {"role": msg.role, "parts": [msg.content]}
            for msg in self.messages
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert thành dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Tạo Conversation từ dictionary."""
        return cls(
            id=data["id"],
            title=data.get("title", "New Conversation"),
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )


# ============================================================
# Conversation Manager
# ============================================================

class ConversationManager:
    """
    Quản lý multiple conversation sessions.

    Cung cấp:
    - Tạo/xóa/switch conversations
    - Lưu/load conversations từ disk
    - Auto-save functionality
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Khởi tạo ConversationManager.

        Args:
            storage_path: Đường dẫn lưu conversations (mặc định trong data/conversations)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = config.DATA_DIR / "conversations"

        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Active conversations (in-memory)
        self.conversations: Dict[str, Conversation] = {}

        # Current active conversation ID
        self._current_id: Optional[str] = None

        # Load existing conversations
        self._load_index()

        print(f"[ConversationManager] Initialized at {self.storage_path}")

    def _load_index(self) -> None:
        """Load index của all conversations."""
        index_file = self.storage_path / "index.json"

        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.conversations = {
                    cid: Conversation.from_dict(cdata)
                    for cid, cdata in data.items()
                }
            print(f"[ConversationManager] Loaded {len(self.conversations)} conversations")

    def _save_index(self) -> None:
        """Save index của all conversations."""
        index_file = self.storage_path / "index.json"

        data = {
            cid: conv.to_dict()
            for cid, conv in self.conversations.items()
        }

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_conversation(
        self,
        title: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Conversation:
        """
        Tạo conversation mới.

        Args:
            title: Tiêu đề (auto-generated nếu None)
            metadata: Metadata bổ sung

        Returns:
            Conversation instance mới
        """
        conv_id = str(uuid.uuid4())[:8]
        title = title or f"Conversation {len(self.conversations) + 1}"

        conv = Conversation(
            id=conv_id,
            title=title,
            metadata=metadata or {}
        )

        self.conversations[conv_id] = conv
        self._current_id = conv_id
        self._save_index()

        print(f"[ConversationManager] Created conversation: {conv_id} - {title}")
        return conv

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.conversations.get(conv_id)

    def get_current(self) -> Optional[Conversation]:
        """Get current active conversation."""
        if self._current_id:
            return self.conversations.get(self._current_id)
        return None

    def switch_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Switch sang conversation khác."""
        if conv_id in self.conversations:
            self._current_id = conv_id
            print(f"[ConversationManager] Switched to: {conv_id}")
            return self.conversations[conv_id]
        return None

    def delete_conversation(self, conv_id: str) -> bool:
        """Xóa conversation."""
        if conv_id in self.conversations:
            del self.conversations[conv_id]

            if self._current_id == conv_id:
                self._current_id = None

            self._save_index()
            print(f"[ConversationManager] Deleted conversation: {conv_id}")
            return True
        return False

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List tất cả conversations (summary)."""
        return [
            {
                "id": conv.id,
                "title": conv.title,
                "num_messages": len(conv.messages),
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "is_active": conv.id == self._current_id
            }
            for conv in self.conversations.values()
        ]

    def rename_conversation(self, conv_id: str, new_title: str) -> bool:
        """Đổi tên conversation."""
        conv = self.conversations.get(conv_id)
        if conv:
            conv.title = new_title
            conv.updated_at = datetime.now().isoformat()
            self._save_index()
            return True
        return False

    def save_conversation(self, conv_id: str) -> bool:
        """Save một conversation cụ thể."""
        conv = self.conversations.get(conv_id)
        if conv:
            conv_file = self.storage_path / f"{conv_id}.json"
            with open(conv_file, "w", encoding="utf-8") as f:
                json.dump(conv.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"[ConversationManager] Saved: {conv_id}")
            return True
        return False


# ============================================================
# Gemini Chatbot với Memory & Streaming
# ============================================================

class GeminiChatbot:
    """
    Enhanced Chatbot wrapper cho Google Gemini API.

    Tính năng:
    - Streaming response support
    - Conversation memory với auto-summarization
    - Multiple sessions management
    - Error handling & retry logic
    - Configurable generation parameters

    Attributes:
        model: Gemini GenerativeModel instance
        conversation: Current Conversation instance
        conversation_manager: Manager cho multiple sessions
    """

    # Maximum messages trước khi auto-summarize
    MAX_MESSAGES_BEFORE_SUMMARY = 20

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        enable_streaming: bool = True,
        enable_memory: bool = True,
        auto_save: bool = True
    ):
        """
        Khởi tạo Gemini Chatbot.

        Args:
            model_name: Tên model Gemini (mặc định từ config)
            temperature: Độ ngẫu nhiên của response (0.0-1.0)
            max_tokens: Số tokens tối đa trong response
            system_prompt: System prompt để set context
            conversation_id: ID của conversation (tạo mới nếu None)
            enable_streaming: Bật streaming response
            enable_memory: Bật conversation memory
            auto_save: Tự động save conversations
        """
        # Configure Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)

        # Store configuration
        self.model_name = model_name or config.GEMINI_MODEL_NAME
        self.temperature = temperature if temperature is not None else config.GEMINI_TEMPERATURE
        self.max_tokens = max_tokens or config.GEMINI_MAX_TOKENS
        self.enable_streaming = enable_streaming
        self.enable_memory = enable_memory
        self.auto_save = auto_save

        # System prompt
        self.system_prompt = system_prompt

        # Initialize model
        self._init_model()

        # Conversation management
        self.conversation_manager = ConversationManager()
        self.conversation = self.conversation_manager.get_conversation(conversation_id)

        if self.conversation is None:
            self.conversation = self.conversation_manager.create_conversation()

        # Memory (summary of older messages)
        self._memory_summary: Optional[str] = None

        print(f"[GeminiChatbot] Initialized with model: {self.model_name}")
        print(f"[GeminiChatbot] Conversation: {self.conversation.id} - {self.conversation.title}")

    def _init_model(self) -> None:
        """Initialize Gemini model."""
        self.model = GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )

    def _get_generation_config(self) -> Any:
        """Get generation config cho API call."""
        return genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            top_p=config.GEMINI_TOP_P,
            top_k=config.GEMINI_TOP_K
        )

    def _should_summarize(self) -> bool:
        """Kiểm tra xem nên summarize memory chưa."""
        return (
            self.enable_memory and
            len(self.conversation.messages) >= self.MAX_MESSAGES_BEFORE_SUMMARY
        )

    def _summarize_history(self) -> str:
        """
        Summarize conversation history để tiết kiệm context.

        Returns:
            Summary text
        """
        if len(self.conversation.messages) < 4:
            return ""

        # Get last N messages for summarization
        recent_msgs = self.conversation.messages[-10:]
        summary_prompt = (
            "Summarize the following conversation briefly in 2-3 sentences. "
            "Focus on the key topics and questions discussed:\n\n"
            + "\n".join([f"{m.role}: {m.content[:100]}" for m in recent_msgs])
        )

        try:
            summary = self.model.generate_content(summary_prompt)
            self._memory_summary = summary.text

            # Keep only last 5 messages
            self.conversation.messages = self.conversation.messages[-5:]

            # Add summary as system message
            self.conversation.add_message(
                role="system",
                content=f"[Previous context summary]: {summary.text}",
                metadata={"is_summary": True}
            )

            print(f"[GeminiChatbot] Summarized {len(recent_msgs)} messages")
            return summary.text

        except Exception as e:
            print(f"[GeminiChatbot] Summarization failed: {e}")
            return ""

    def chat(
        self,
        message: str,
        clear_history: bool = False,
        retry_on_error: bool = True
    ) -> str:
        """
        Gửi message và nhận response từ Gemini.

        Args:
            message: User message
            clear_history: Nếu True, xóa history trước khi chat
            retry_on_error: Retry nếu API call fails

        Returns:
            Response text từ Gemini
        """
        if clear_history:
            self.conversation_manager.delete_conversation(self.conversation.id)
            self.conversation = self.conversation_manager.create_conversation()
            self._memory_summary = None

        # Check if should summarize
        if self._should_summarize():
            self._summarize_history()

        # Add user message
        self.conversation.add_message(role="user", content=message)

        # Prepare API call
        messages_for_api = self.conversation.get_messages_for_api()

        # Try API call with retry
        max_retries = 3 if retry_on_error else 1
        last_error = None

        for attempt in range(max_retries):
            try:
                # Start chat session
                chat_session = self.model.start_chat(history=messages_for_api[:-1] if messages_for_api else [])

                # Send message
                response = chat_session.send_message(
                    message,
                    generation_config=self._get_generation_config()
                )

                # Add model response
                self.conversation.add_message(role="model", content=response.text)

                # Auto-save
                if self.auto_save:
                    self.conversation_manager.save_conversation(self.conversation.id)

                return response.text

            except GoogleAPIError as e:
                last_error = e
                print(f"[GeminiChatbot] API error (attempt {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue

            except Exception as e:
                last_error = e
                print(f"[GeminiChatbot] Unexpected error: {e}")
                break

        # All retries failed
        error_msg = f"Failed after {max_retries} attempts: {last_error}"
        print(f"[GeminiChatbot] {error_msg}")

        # Remove failed user message
        if self.conversation.messages and self.conversation.messages[-1].role == "user":
            self.conversation.messages.pop()

        raise RuntimeError(error_msg)

    def stream_chat(
        self,
        message: str,
        callback: Optional[Callable[[str], None]] = None,
        clear_history: bool = False
    ) -> Iterator[str]:
        """
        Gửi message và nhận streaming response.

        Args:
            message: User message
            callback: Optional callback được gọi với mỗi chunk
            clear_history: Nếu True, xóa history trước

        Yields:
            Response chunks as they arrive
        """
        if clear_history:
            self.conversation_manager.delete_conversation(self.conversation.id)
            self.conversation = self.conversation_manager.create_conversation()

        # Check summarization
        if self._should_summarize():
            self._summarize_history()

        # Add user message
        self.conversation.add_message(role="user", content=message)

        try:
            # Generate with streaming
            messages_for_api = self.conversation.get_messages_for_api()
            chat_session = self.model.start_chat(history=messages_for_api[:-1])

            response_stream = chat_session.send_message(
                message,
                generation_config=self._get_generation_config(),
                stream=True
            )

            # Collect full response
            full_response = ""

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text

                    if callback:
                        callback(chunk.text)

                    yield chunk.text

            # Add complete response to history
            if full_response:
                self.conversation.add_message(role="model", content=full_response)

                if self.auto_save:
                    self.conversation_manager.save_conversation(self.conversation.id)

        except Exception as e:
            error_msg = f"Streaming failed: {e}"
            print(f"[GeminiChatbot] {error_msg}")

            if self.conversation.messages and self.conversation.messages[-1].role == "user":
                self.conversation.messages.pop()

            yield f"[Error: {error_msg}]"

    def generate(self, prompt: str, retry_on_error: bool = True) -> str:
        """
        Generate text từ prompt (non-chat, single-shot).

        Args:
            prompt: Prompt text
            retry_on_error: Retry nếu fails

        Returns:
            Generated text
        """
        max_retries = 3 if retry_on_error else 1
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self._get_generation_config()
                )
                return response.text

            except GoogleAPIError as e:
                last_error = e
                print(f"[GeminiChatbot] API error (attempt {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue

            except Exception as e:
                last_error = e
                break

        raise RuntimeError(f"Generate failed after {max_retries} attempts: {last_error}")

    def generate_stream(
        self,
        prompt: str,
        callback: Optional[Callable[[str], None]] = None
    ) -> Iterator[str]:
        """
        Generate text với streaming.

        Args:
            prompt: Prompt text
            callback: Optional callback for each chunk

        Yields:
            Response chunks
        """
        try:
            response_stream = self.model.generate_content(
                prompt,
                generation_config=self._get_generation_config(),
                stream=True
            )

            full_response = ""

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text

                    if callback:
                        callback(chunk.text)

                    yield chunk.text

        except Exception as e:
            yield f"[Error: {e}]"

    def clear_history(self) -> None:
        """Xóa conversation history."""
        old_id = self.conversation.id
        self.conversation_manager.delete_conversation(old_id)
        self.conversation = self.conversation_manager.create_conversation()
        self._memory_summary = None
        print(f"[GeminiChatbot] History cleared, new conversation: {self.conversation.id}")

    def get_history(self) -> List[Message]:
        """Trả về conversation history."""
        return self.conversation.messages.copy()

    def new_conversation(self, title: Optional[str] = None) -> Conversation:
        """Tạo conversation mới."""
        self.conversation = self.conversation_manager.create_conversation(title=title)
        self._memory_summary = None
        return self.conversation

    def switch_conversation(self, conv_id: str) -> bool:
        """Switch sang conversation khác."""
        conv = self.conversation_manager.switch_conversation(conv_id)
        if conv:
            self.conversation = conv
            return True
        return False

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations."""
        return self.conversation_manager.list_conversations()

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        return {
            "conversation_id": self.conversation.id,
            "conversation_title": self.conversation.title,
            "num_messages": len(self.conversation.messages),
            "memory_summary": self._memory_summary,
            "model": self.model_name,
            "temperature": self.temperature,
            "enable_streaming": self.enable_streaming,
            "enable_memory": self.enable_memory
        }


# ============================================================
# RAG Chatbot với Enhanced Features
# ============================================================

class RAGChatbot(GeminiChatbot):
    """
    Enhanced RAG Chatbot.

    Kế thừa từ GeminiChatbot với RAG-specific features:
    - Chat với context từ retrieval
    - Source citations
    - Streaming support cho RAG
    """

    def __init__(self, system_prompt: Optional[str] = None, **kwargs):
        """
        Khởi tạo RAG Chatbot.

        Args:
            system_prompt: System prompt cho RAG
            **kwargs: Arguments cho parent class
        """
        if system_prompt is None:
            system_prompt = (
                "Bạn là một trợ lý AI hữu ích, chuyên trả lời câu hỏi dựa trên "
                "thông tin được cung cấp trong context. "
                "Nếu không có thông tin trong context để trả lời, hãy nói rõ rằng "
                "bạn không tìm thấy thông tin liên quan. "
                "Trả lời bằng tiếng Việt."
            )

        super().__init__(system_prompt=system_prompt, **kwargs)

    def chat_with_context(
        self,
        message: str,
        contexts: List[str],
        citation_threshold: float = 0.0,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Chat với context từ retrieval.

        Args:
            message: User question
            contexts: List của relevant text chunks
            citation_threshold: Minimum threshold cho citations
            include_sources: Có include full source content không

        Returns:
            Dict chứa 'answer', 'sources', 'metadata'
        """
        # Format context
        if contexts:
            context_text = "\n\n".join([
                f"[Document {i+1}]:\n{ctx}" for i, ctx in enumerate(contexts)
            ])
            full_prompt = (
                f"=== CONTEXT INFORMATION ===\n{context_text}\n\n"
                f"=== USER QUESTION ===\n{message}\n\n"
                f"=== INSTRUCTIONS ===\n"
                f"Hãy trả lời câu hỏi dựa trên context ở trên. "
                f"Nếu câu trả lời có trong context, hãy trích dẫn rõ ràng. "
                f"Nếu không có thông tin, hãy nói rõ."
            )
        else:
            full_prompt = message

        # Generate response
        response_text = self.chat(full_prompt)

        # Build sources
        sources = []
        for i, ctx in enumerate(contexts):
            source = {
                "document_id": i + 1,
                "content_preview": ctx[:200] + "..." if len(ctx) > 200 else ctx
            }

            if include_sources:
                source["full_content"] = ctx

            sources.append(source)

        return {
            "answer": response_text,
            "sources": sources,
            "num_contexts_used": len(contexts),
            "question": message
        }

    def stream_chat_with_context(
        self,
        message: str,
        contexts: List[str],
        callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Chat với context và streaming response.

        Args:
            message: User question
            contexts: List của relevant text chunks
            callback: Callback cho streaming chunks

        Returns:
            Dict với answer và sources
        """
        # Format context
        if contexts:
            context_text = "\n\n".join([
                f"[Document {i+1}]:\n{ctx}" for i, ctx in enumerate(contexts)
            ])
            full_prompt = (
                f"=== CONTEXT ===\n{context_text}\n\n"
                f"=== QUESTION ===\n{message}\n\n"
                f"Trả lời dựa trên context:"
            )
        else:
            full_prompt = message

        # Stream response
        chunks = []
        for chunk in self.stream_chat(full_prompt, callback=callback):
            chunks.append(chunk)

        full_response = "".join(chunks)

        # Build sources (same as non-streaming)
        sources = [
            {
                "document_id": i + 1,
                "content_preview": ctx[:200] + "..." if len(ctx) > 200 else ctx
            }
            for i, ctx in enumerate(contexts)
        ]

        return {
            "answer": full_response,
            "sources": sources,
            "num_contexts_used": len(contexts),
            "question": message
        }


# ============================================================
# Utility Functions
# ============================================================

def list_available_models() -> List[str]:
    """
    Liệt kê các Gemini models có sẵn.

    Returns:
        List of available model names
    """
    genai.configure(api_key=config.GEMINI_API_KEY)
    models = genai.list_models()
    return [m.name for m in models if 'generateContent' in m.supported_generation_methods]


def test_api_connection() -> bool:
    """
    Test xem API connection có hoạt động không.

    Returns:
        True nếu kết nối thành công
    """
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        models = list(genai.list_models())
        return len(models) > 0
    except Exception:
        return False


# ============================================================
# Module-level Test
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Enhanced Gemini Chatbot Module")
    print("=" * 60)

    try:
        # Validate config
        config.validate_config()

        # Test API connection
        print("\n[TEST 0] API Connection Test")
        print("-" * 40)
        if test_api_connection():
            print("API connection: OK")
            models = list_available_models()
            print(f"Available models: {len(models)}")
            print(f"Models: {models[:3]}...")
        else:
            print("API connection: FAILED")
            print("Please check your API key")
            sys.exit(1)

        # Test 1: Basic Chat
        print("\n[TEST 1] Basic Chat")
        print("-" * 40)
        chatbot = GeminiChatbot(temperature=0.7)

        response = chatbot.chat("Xin chào! Bạn là AI gì?")
        print(f"User: Xin chào! Bạn là AI gì?")
        print(f"Bot: {response[:200]}...")

        # Test 2: Streaming Chat
        print("\n[TEST 2] Streaming Chat")
        print("-" * 40)
        print("User: Kể một câu chuyện ngắn")
        print("Bot (streaming): ", end="", flush=True)

        response_chunks = []
        for chunk in chatbot.stream_chat("Kể một câu chuyện cổ tích ngắn"):
            print(chunk, end="", flush=True)
            response_chunks.append(chunk)

        print("\n")

        # Test 3: Conversation Management
        print("\n[TEST 3] Conversation Management")
        print("-" * 40)

        # Create new conversation
        new_conv = chatbot.new_conversation("Test Conversation")
        print(f"Created: {new_conv.id} - {new_conv.title}")

        # List conversations
        convs = chatbot.list_conversations()
        print(f"Total conversations: {len(convs)}")

        # Test stats
        stats = chatbot.get_stats()
        print(f"Current stats: {stats['num_messages']} messages")

        # Test 4: RAG Chat
        print("\n[TEST 4] RAG Chat with Context")
        print("-" * 40)
        rag_bot = RAGChatbot()

        test_contexts = [
            "Python là một ngôn ngữ lập trình bậc cao, thông dịch, đa năng. "
            "Nó được tạo ra bởi Guido van Rossum và phát hành lần đầu năm 1991.",

            "Python hỗ trợ nhiều paradigm lập trình như lập trình hướng đối tượng (OOP), "
            "lập trình hàm (functional), và lập trình thủ tục (procedural).",

            "Python có cú pháp rất dễ đọc, sử dụng indentation thay vì dấu ngoặc nhọn. "
            "Điều này làm cho code Python dễ hiểu và maintain."
        ]

        result = rag_bot.chat_with_context(
            "Python được tạo ra khi nào và bởi ai?",
            contexts=test_contexts
        )

        print(f"Q: Python được tạo ra khi nào và bởi ai?")
        print(f"A: {result['answer']}")
        print(f"Sources used: {result['num_contexts_used']}")

        # Test 5: Memory Feature
        print("\n[TEST 5] Memory Feature")
        print("-" * 40)

        # Simulate long conversation
        print("Simulating multiple messages...")
        memory_bot = GeminiChatbot(enable_memory=True)

        for i in range(5):
            memory_bot.chat(f"Message {i+1}: Đây là test message number {i+1}")

        stats = memory_bot.get_stats()
        print(f"After 5 messages: {stats['num_messages']} messages in conversation")

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except ValueError as e:
        print(f"\n[CONFIG ERROR] {e}")
        print("\nVui lòng tạo file .env với:")
        print("GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
