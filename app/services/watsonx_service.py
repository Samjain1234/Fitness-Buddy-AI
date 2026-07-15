"""
IBM Watsonx.ai service.
All AI/LLM calls go through this single module.
Uses the ibm-watsonx-ai SDK with the Granite foundation model.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from app.config import AGENT_INSTRUCTIONS, Settings

logger = logging.getLogger(__name__)


class WatsonxService:
    """
    Wraps IBM Watsonx.ai text generation.
    Lazy-initialises the ModelInference client on first call.
    The client is NOT cached after a failed init so that restarting
    the server after fixing credentials recovers correctly.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Optional[Any] = None
        self._configured = bool(
            settings.ibm_cloud_api_key
            and settings.ibm_cloud_api_key not in ("your_ibm_cloud_api_key_here", "")
            and settings.watsonx_project_id
            and settings.watsonx_project_id not in ("your_watsonx_project_id_here", "")
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> Any:
        """Lazy-init and cache the Watsonx ModelInference client."""
        if self._client is not None:
            return self._client

        if not self._configured:
            raise RuntimeError(
                "IBM Watsonx.ai credentials are not configured. "
                "Set IBM_CLOUD_API_KEY and WATSONX_PROJECT_ID in your .env file."
            )

        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
        except ImportError as exc:
            raise ImportError(
                "ibm-watsonx-ai package is not installed. "
                "Run: pip install ibm-watsonx-ai"
            ) from exc

        logger.info(
            "Initialising Watsonx client — url=%s model=%s project=%s…",
            self.settings.watsonx_url,
            self.settings.watsonx_model_id,
            self.settings.watsonx_project_id[:8] + "…",  # partial for safety
        )

        # This call fetches an IAM token — raises WMLClientError on bad key
        credentials = Credentials(
            url=self.settings.watsonx_url,
            api_key=self.settings.ibm_cloud_api_key,
        )

        params = {
            GenParams.MAX_NEW_TOKENS: self.settings.watsonx_max_tokens,
            GenParams.TEMPERATURE: self.settings.watsonx_temperature,
            GenParams.TOP_P: self.settings.watsonx_top_p,
            GenParams.REPETITION_PENALTY: 1.1,
        }

        # ModelInference may also validate the project_id here
        client = ModelInference(
            model_id=self.settings.watsonx_model_id,
            credentials=credentials,
            project_id=self.settings.watsonx_project_id,
            params=params,
        )

        # Only cache after full success
        self._client = client
        logger.info("✅ Watsonx client ready — model: %s", self.settings.watsonx_model_id)
        return self._client

    def _build_prompt(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_context: Optional[str] = None,
    ) -> str:
        """
        Build a Granite-compatible chat prompt.
        Granite 3.x instruction-tuned models use the
        <|system|> / <|user|> / <|assistant|> chat format.
        """
        lines: List[str] = []

        # System block
        system_text = AGENT_INSTRUCTIONS
        if system_context:
            system_text += f"\n\n## User Context\n{system_context}"
        lines.append(f"<|system|>\n{system_text.strip()}\n<|end_of_text|>")

        # Conversation history (last 10 turns to stay within context window)
        if conversation_history:
            for turn in conversation_history[-10:]:
                role = turn.get("role", "user")
                content = turn.get("content", "").strip()
                if content:
                    lines.append(f"<|{role}|>\n{content}\n<|end_of_text|>")

        # Current user message
        lines.append(f"<|user|>\n{user_message.strip()}\n<|end_of_text|>")
        lines.append("<|assistant|>")

        return "\n".join(lines)

    @staticmethod
    def _clean_response(text: str) -> str:
        """Strip residual Granite control tokens from the generated output."""
        for token in (
            "<|end_of_text|>", "<|end|>",
            "<|user|>", "<|assistant|>", "<|system|>",
        ):
            text = text.replace(token, "")
        return text.strip()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_configured(self) -> bool:
        return self._configured

    async def generate(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from the Granite model.
        Returns a dict with 'text', 'tokens_used', and 'model_id'.

        Error handling strategy:
          - Credentials not set   → friendly "not configured" message
          - IAM / network error   → detailed error logged + user-friendly message
          - Any other exception   → logged with full traceback
        """
        if not self._configured:
            return {
                "text": (
                    "⚠️ **IBM Watsonx.ai credentials are not configured.**\n\n"
                    "Please add the following to your `.env` file and restart the server:\n"
                    "```\n"
                    "IBM_CLOUD_API_KEY=your_actual_api_key\n"
                    "WATSONX_PROJECT_ID=your_actual_project_id\n"
                    "```\n"
                    "Get your API key from https://cloud.ibm.com/iam/apikeys"
                ),
                "tokens_used": 0,
                "model_id": "not-configured",
            }

        try:
            client = self._get_client()
            prompt = self._build_prompt(user_message, conversation_history, system_context)

            # ModelInference.generate is synchronous — run in thread pool
            loop = asyncio.get_event_loop()
            result: Dict[str, Any] = await loop.run_in_executor(
                None,
                lambda: client.generate(prompt=prompt),
            )

            generated_text = self._clean_response(
                result["results"][0]["generated_text"]
            )
            tokens_used: int = result["results"][0].get("generated_token_count", 0)

            logger.debug("Generated %d tokens for message: %.60s…", tokens_used, user_message)

            return {
                "text": generated_text,
                "tokens_used": tokens_used,
                "model_id": self.settings.watsonx_model_id,
            }

        except Exception as exc:
            # Reset cached client so the next request retries the connection
            self._client = None

            error_type = type(exc).__name__
            error_msg = str(exc)

            # Log the full traceback for server-side diagnosis
            logger.exception("Watsonx generation error [%s]: %s", error_type, error_msg)

            # Build a user-facing message that explains the actual problem
            user_msg = _friendly_error(error_type, error_msg)

            return {
                "text": user_msg,
                "tokens_used": 0,
                "model_id": "error",
                "error": error_msg,
            }

    async def generate_workout_plan(
        self,
        profile_context: str,
        workout_request: str,
    ) -> str:
        result = await self.generate(
            user_message=workout_request,
            system_context=f"User Profile Context:\n{profile_context}",
        )
        return result["text"]

    async def generate_nutrition_advice(self, context: str) -> str:
        result = await self.generate(
            user_message="Please provide a detailed personalised nutrition plan and advice.",
            system_context=context,
        )
        return result["text"]

    async def generate_motivation(self, context: str) -> str:
        result = await self.generate(
            user_message=(
                "Give me a powerful, personalised motivational message to keep me going "
                "on my fitness journey today. Make it specific, uplifting, and actionable."
            ),
            system_context=context,
        )
        return result["text"]


# ------------------------------------------------------------------
# Helper — map SDK exceptions to plain-English messages
# ------------------------------------------------------------------

def _friendly_error(error_type: str, error_msg: str) -> str:
    """Return a helpful, actionable error message for the chat UI."""
    msg_lower = error_msg.lower()

    if "400" in error_msg or "iam token" in msg_lower or "iam" in msg_lower:
        return (
            "❌ **IBM Cloud authentication failed (400).**\n\n"
            "Your `IBM_CLOUD_API_KEY` is being rejected by IBM IAM. Please:\n\n"
            "1. Go to https://cloud.ibm.com/iam/apikeys\n"
            "2. Delete the old key and **create a new one**\n"
            "3. Update `IBM_CLOUD_API_KEY` in your `.env` file (no quotes, no spaces)\n"
            "4. Make sure `WATSONX_URL` matches your project's region\n"
            "5. Restart the server\n\n"
            "💡 **Common mistakes:** trailing spaces, copying `your_ibm_cloud_api_key_here` "
            "instead of the real key, or using an expired/deleted key."
        )

    if "401" in error_msg or "unauthorized" in msg_lower:
        return (
            "❌ **Unauthorised (401).** Your API key was accepted but lacks permission "
            "to access this Watsonx project.\n\n"
            "Check that the key has **Editor** or **Viewer** access on your Watsonx.ai project "
            "at https://dataplatform.cloud.ibm.com"
        )

    if "403" in error_msg or "forbidden" in msg_lower:
        return (
            "❌ **Forbidden (403).** Your account may not have Watsonx.ai access enabled.\n\n"
            "Make sure you have an active **IBM Watsonx.ai** service instance in your IBM Cloud account."
        )

    if "404" in error_msg or "not found" in msg_lower:
        return (
            "❌ **Project not found (404).** `WATSONX_PROJECT_ID` is incorrect or the project "
            "was deleted.\n\nDouble-check the Project ID from "
            "https://dataplatform.cloud.ibm.com → your project → Manage tab."
        )

    if "connectionerror" in error_type.lower() or "timeout" in msg_lower or "connect" in msg_lower:
        return (
            "❌ **Network error.** Cannot reach IBM Watsonx.ai servers.\n\n"
            "- Check your internet connection\n"
            "- Verify `WATSONX_URL` in `.env` is correct for your region\n"
            "- Try again in a moment"
        )

    if "importerror" in error_type.lower() or "module" in msg_lower:
        return (
            "❌ **ibm-watsonx-ai not installed.**\n\n"
            "Run: `pip install ibm-watsonx-ai` then restart the server."
        )

    # Fallback — show the raw error so it's diagnosable
    return (
        f"❌ **AI service error** `{error_type}`\n\n"
        f"```\n{error_msg[:400]}\n```\n\n"
        "Check the server logs for the full traceback. "
        "Common fixes: verify `.env` credentials and restart the server."
    )
