import os
import requests
from typing import Protocol
from config.settings import Config


class AIProvider(Protocol):
    """AI Provider interface"""

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        """Generate text from prompt"""
        ...


class AnthropicProvider:
    """Anthropic Claude provider"""

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text


class OllamaProvider:
    """Ollama local LLM provider"""

    def __init__(self):
        self.url = Config.OLLAMA_URL
        self.model = Config.OLLAMA_MODEL

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        print(f"Calling Ollama ({self.model}) with prompt length: {len(prompt)} chars, max_tokens: {max_tokens}")

        try:
            response = requests.post(
                f'{self.url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'num_predict': max_tokens,
                        'temperature': 0.7
                    }
                },
                timeout=Config.OLLAMA_TIMEOUT  # Configurable timeout for Ollama requests
            )
            response.raise_for_status()
            result = response.json()

            print(f"Ollama response received. Length: {len(result['response'])} chars")
            return result['response']

        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out after {Config.OLLAMA_TIMEOUT} seconds. The model '{self.model}' may be too slow for this task. Consider using a faster model or increasing OLLAMA_TIMEOUT.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")


class OpenAIProvider:
    """OpenAI GPT provider"""

    def __init__(self):
        import openai
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


def get_ai_provider() -> AIProvider:
    """Get configured AI provider"""
    provider = Config.AI_PROVIDER.lower()

    if provider == 'anthropic':
        return AnthropicProvider()
    elif provider == 'ollama':
        return OllamaProvider()
    elif provider == 'openai':
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider}")