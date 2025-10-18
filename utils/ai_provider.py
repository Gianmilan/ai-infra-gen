import requests
import logging
from typing import Protocol
from config.settings import Config

logger = logging.getLogger(__name__)


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
        logger.info("Initialized AnthropicProvider with Claude 3.5 Sonnet")

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        logger.info(f"Calling Anthropic API (prompt: {len(prompt)} chars, max_tokens: {max_tokens})")
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            logger.info(f"Anthropic API response received (length: {len(response_text)} chars, "
                        f"usage: input={message.usage.input_tokens}, output={message.usage.output_tokens})")
            return response_text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}", exc_info=True)
            raise


class OllamaProvider:
    """Ollama local LLM provider"""

    def __init__(self):
        self.url = Config.OLLAMA_URL
        self.model = Config.OLLAMA_MODEL
        logger.info(f"Initialized OllamaProvider (url: {self.url}, model: {self.model})")

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        logger.info(f"Calling Ollama API (model: {self.model}, prompt: {len(prompt)} chars, max_tokens: {max_tokens})")

        try:
            import time
            start_time = time.time()

            response = requests.post(
                f'{self.url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'keep_alive': '5m',
                    'options': {
                        'num_predict': max_tokens,
                        'temperature': 0.7
                    }
                },
                timeout=Config.OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()

            duration = time.time() - start_time
            response_text = result['response']

            # Log additional Ollama metrics if available
            metrics = {
                'duration': duration,
                'response_length': len(response_text)
            }
            if 'total_duration' in result:
                metrics['total_duration_ns'] = result['total_duration']
            if 'load_duration' in result:
                metrics['load_duration_ns'] = result['load_duration']
            if 'prompt_eval_count' in result:
                metrics['prompt_tokens'] = result['prompt_eval_count']
            if 'eval_count' in result:
                metrics['completion_tokens'] = result['eval_count']

            logger.info(f"Ollama API response received in {duration:.2f}s: {metrics}")
            return response_text

        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {Config.OLLAMA_TIMEOUT}s (model: {self.model})")
            raise Exception(
                f"Ollama request timed out after {Config.OLLAMA_TIMEOUT} seconds. The model '{self.model}' may be too slow for this task. Consider using a faster model or increasing OLLAMA_TIMEOUT.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request error: {str(e)}", exc_info=True)
            raise Exception(f"Ollama API error: {str(e)}")


class OpenAIProvider:
    """OpenAI GPT provider"""

    def __init__(self):
        import openai
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai
        logger.info("Initialized OpenAIProvider with GPT-4 Turbo")

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        logger.info(f"Calling OpenAI API (prompt: {len(prompt)} chars, max_tokens: {max_tokens})")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            response_text = response.choices[0].message.content
            logger.info(f"OpenAI API response received (length: {len(response_text)} chars, "
                        f"usage: input={response.usage.prompt_tokens}, output={response.usage.completion_tokens})")
            return response_text
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise


def get_ai_provider() -> AIProvider:
    """Get configured AI provider"""
    provider = Config.AI_PROVIDER.lower()
    logger.info(f"Instantiating AI provider: {provider}")

    if provider == 'anthropic':
        return AnthropicProvider()
    elif provider == 'ollama':
        return OllamaProvider()
    elif provider == 'openai':
        return OpenAIProvider()
    else:
        logger.error(f"Invalid AI provider requested: {provider}")
        raise ValueError(f"Unknown AI provider: {provider}")
