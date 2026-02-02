"""OpenAI-compatible provider for NVIDIA API and other custom endpoints."""

from typing import Any

from openai import AsyncOpenAI

from nanobot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


class OpenAIProvider(LLMProvider):
    """
    LLM provider using native OpenAI SDK for NVIDIA API and OpenAI-compatible endpoints.
    
    Supports streaming, reasoning content (thinking), and custom endpoints like NVIDIA.
    """
    
    def __init__(
        self, 
        api_key: str | None = None, 
        api_base: str | None = None,
        default_model: str = "z-ai/glm4.7"
    ):
        super().__init__(api_key, api_base)
        self.default_model = default_model
        
        # Initialize async OpenAI client
        # NVIDIA API uses base_url instead of api_base
        base_url = api_base or "https://integrate.api.nvidia.com/v1"
        # Support $NVIDIA_API_KEY env var syntax in config
        key = api_key
        if key and key.startswith("$"):
            import os
            key = os.getenv(key[1:], key)
        
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=key or "dummy-key"
        )
    
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 16384,
        temperature: float = 1.0,
        enable_thinking: bool = True,
        **extra_kwargs
    ) -> LLMResponse:
        """
        Send a chat completion request via OpenAI SDK.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions in OpenAI format.
            model: Model identifier (e.g., 'z-ai/glm4.7').
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            enable_thinking: Enable reasoning/thinking mode for supported models.
            **extra_kwargs: Additional parameters to pass to the API.
        
        Returns:
            LLMResponse with content and/or tool calls.
        """
        model = model or self.default_model
        
        # Build request parameters
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,  # Non-streaming for simplicity
        }
        
        # Add extra_body for NVIDIA-specific features (thinking/reasoning)
        if enable_thinking and "glm" in model.lower():
            kwargs["extra_body"] = {
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "clear_thinking": False
                }
            }
        
        # Add tools if provided
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        # Merge any extra kwargs
        kwargs.update(extra_kwargs)
        
        try:
            response = await self.client.chat.completions.create(**kwargs)
            return self._parse_response(response)
        except Exception as e:
            return LLMResponse(
                content=f"Error calling LLM: {str(e)}",
                finish_reason="error",
            )
    
    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse OpenAI SDK response into our standard format."""
        choice = response.choices[0]
        message = choice.message
        
        # Extract content
        content = message.content or ""
        
        # Note: reasoning_content is available in the response but we don't expose it
        # as it's just the model's internal thinking process
        # reasoning_content = getattr(message, "reasoning_content", None)
        
        # Extract tool calls
        tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                args = tc.function.arguments
                if isinstance(args, str):
                    import json
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}
                
                tool_calls.append(ToolCallRequest(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=args,
                ))
        
        # Extract usage
        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
        )
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model
