#!/usr/bin/env python3
"""
DevForge - AI Provider Module
Unified interface for multiple AI providers (OpenAI, Anthropic, Gemini, Minimax, Moonshot, Ollama)
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Generator
from pathlib import Path

class AIProvider:
    """Unified AI provider interface"""
    
    def __init__(self, config_path: str = "config/.env"):
        self.config = self._load_config(config_path)
        self.provider_configs = self._setup_providers()
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration from .env file"""
        config = {}
        env_path = Path(path)
        
        # Load from file
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key] = value.strip('"').strip("'")
        
        # Environment variables override
        for key in os.environ:
            config[key] = os.environ[key]
        
        return config
    
    def _setup_providers(self) -> Dict:
        """Setup all available providers"""
        providers = {}
        
        # OpenAI
        if self.config.get('OPENAI_API_KEY'):
            providers['openai'] = {
                'api_key': self.config['OPENAI_API_KEY'],
                'base_url': self.config.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
                'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'default_model': 'gpt-4o'
            }
        
        # Anthropic
        if self.config.get('ANTHROPIC_API_KEY'):
            providers['anthropic'] = {
                'api_key': self.config['ANTHROPIC_API_KEY'],
                'base_url': self.config.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1'),
                'models': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
                'default_model': 'claude-3-5-sonnet-20241022'
            }
        
        # Gemini
        if self.config.get('GEMINI_API_KEY'):
            providers['gemini'] = {
                'api_key': self.config['GEMINI_API_KEY'],
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'models': ['gemini-1.5-pro', 'gemini-1.5-flash'],
                'default_model': 'gemini-1.5-pro'
            }
        
        # Minimax
        if self.config.get('MINIMAX_API_KEY'):
            providers['minimax'] = {
                'api_key': self.config['MINIMAX_API_KEY'],
                'group_id': self.config.get('MINIMAX_GROUP_ID', ''),
                'base_url': self.config.get('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1'),
                'models': ['abab6.5s-chat', 'abab6-chat', 'abab5.5-chat'],
                'default_model': 'abab6.5s-chat'
            }
        
        # Moonshot
        if self.config.get('MOONSHOT_API_KEY'):
            providers['moonshot'] = {
                'api_key': self.config['MOONSHOT_API_KEY'],
                'base_url': self.config.get('MOONSHOT_BASE_URL', 'https://api.moonshot.cn/v1'),
                'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
                'default_model': 'moonshot-v1-8k'
            }
        
        # Ollama (Local)
        if self.config.get('OLLAMA_ENABLED', 'false').lower() == 'true':
            providers['ollama'] = {
                'base_url': self.config.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                'models': self.config.get('OLLAMA_MODELS', 'llama3.2').split(','),
                'default_model': self.config.get('OLLAMA_DEFAULT_MODEL', 'llama3.2'),
                'local': True
            }
        
        return providers
    
    def list_available_providers(self) -> List[str]:
        """List all configured providers"""
        return list(self.provider_configs.keys())
    
    def get_provider_for_agent(self, agent_name: str) -> tuple:
        """Get the configured provider for a specific agent"""
        config_map = {
            'pm': ('PM_AGENT_MODEL', 'PM_AGENT_MODEL_NAME'),
            'reverse_engineer': ('REVERSE_ENGINEER_MODEL', 'REVERSE_ENGINEER_MODEL_NAME'),
            'dev': ('DEV_AGENT_MODEL', 'DEV_AGENT_MODEL_NAME'),
            'qa': ('QA_AGENT_MODEL', 'QA_AGENT_MODEL_NAME'),
            'deploy': ('DEPLOY_AGENT_MODEL', 'DEPLOY_AGENT_MODEL_NAME'),
            'web_scraper': ('WEB_SCRAPER_MODEL', 'WEB_SCRAPER_MODEL_NAME')
        }
        
        model_key, name_key = config_map.get(agent_name, ('FALLBACK_MODEL', 'FALLBACK_MODEL_NAME'))
        
        provider = self.config.get(model_key, 'ollama')
        model_name = self.config.get(name_key)
        
        # If provider not available, use fallback
        if provider not in self.provider_configs:
            fallback = self.config.get('FALLBACK_MODEL', 'ollama')
            provider = fallback if fallback in self.provider_configs else 'openai'
            model_name = None
        
        return provider, model_name
    
    def chat(self, messages: List[Dict], provider: Optional[str] = None, 
             model: Optional[str] = None, temperature: float = 0.7,
             max_tokens: int = 4096) -> str:
        """
        Send chat completion request
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            provider: Provider to use (openai, anthropic, etc.)
            model: Specific model name
            temperature: Creativity parameter
            max_tokens: Maximum response length
        
        Returns:
            Generated text response
        """
        if not provider:
            provider = self.list_available_providers()[0] if self.list_available_providers() else None
        
        if not provider or provider not in self.provider_configs:
            raise ValueError(f"Provider '{provider}' not available. Available: {self.list_available_providers()}")
        
        config = self.provider_configs[provider]
        model = model or config.get('default_model')
        
        # Route to appropriate provider
        if provider == 'openai':
            return self._openai_chat(messages, model, temperature, max_tokens, config)
        elif provider == 'anthropic':
            return self._anthropic_chat(messages, model, temperature, max_tokens, config)
        elif provider == 'gemini':
            return self._gemini_chat(messages, model, temperature, max_tokens, config)
        elif provider == 'minimax':
            return self._minimax_chat(messages, model, temperature, max_tokens, config)
        elif provider == 'moonshot':
            return self._moonshot_chat(messages, model, temperature, max_tokens, config)
        elif provider == 'ollama':
            return self._ollama_chat(messages, model, temperature, max_tokens, config)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _openai_chat(self, messages: List[Dict], model: str, temperature: float, 
                     max_tokens: int, config: Dict) -> str:
        """OpenAI API call"""
        url = f"{config['base_url']}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        return self._make_request(url, payload, headers)
    
    def _anthropic_chat(self, messages: List[Dict], model: str, temperature: float,
                        max_tokens: int, config: Dict) -> str:
        """Anthropic Claude API call"""
        url = f"{config['base_url']}/messages"
        
        # Convert messages to Anthropic format
        system_msg = ""
        user_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_msg = msg['content']
            else:
                user_messages.append(msg)
        
        payload = {
            "model": model,
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": config['api_key'],
            "anthropic-version": "2023-06-01"
        }
        
        return self._make_request(url, payload, headers)
    
    def _gemini_chat(self, messages: List[Dict], model: str, temperature: float,
                     max_tokens: int, config: Dict) -> str:
        """Google Gemini API call"""
        # Convert to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg['role'] == 'user' else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg['content']}]
            })
        
        url = f"{config['base_url']}/models/{model}:generateContent?key={config['api_key']}"
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        return self._make_request(url, payload, headers)
    
    def _minimax_chat(self, messages: List[Dict], model: str, temperature: float,
                      max_tokens: int, config: Dict) -> str:
        """Minimax API call"""
        url = f"{config['base_url']}/text/chatcompletion_v2"
        
        # Format messages for Minimax
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "sender_type": "USER" if msg['role'] == 'user' else "BOT",
                "text": msg['content']
            })
        
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        return self._make_request(url, payload, headers)
    
    def _moonshot_chat(self, messages: List[Dict], model: str, temperature: float,
                       max_tokens: int, config: Dict) -> str:
        """Moonshot AI API call"""
        url = f"{config['base_url']}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        return self._make_request(url, payload, headers)
    
    def _ollama_chat(self, messages: List[Dict], model: str, temperature: float,
                     max_tokens: int, config: Dict) -> str:
        """Ollama local API call"""
        url = f"{config['base_url']}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            return self._make_request(url, payload, headers)
        except Exception as e:
            return f"[Ollama Error: {str(e)}. Make sure Ollama is running with: ollama run {model}]"
    
    def _make_request(self, url: str, payload: Dict, headers: Dict) -> str:
        """Make HTTP request and parse response"""
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Extract text from different response formats
                if 'choices' in result:
                    # OpenAI/Moonshot format
                    return result['choices'][0]['message']['content']
                elif 'content' in result:
                    # Ollama format
                    return result['message']['content']
                elif 'candidates' in result:
                    # Gemini format
                    return result['candidates'][0]['content']['parts'][0]['text']
                elif 'reply' in result:
                    # Minimax format
                    return result['reply']
                else:
                    return str(result)
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"API Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def generate_code(self, prompt: str, language: str = "python", 
                      provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """Specialized code generation"""
        messages = [
            {"role": "system", "content": f"You are an expert {language} developer. Generate clean, well-documented code."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat(messages, provider, model, temperature=0.2, max_tokens=8192)
    
    def analyze_code(self, code: str, task: str = "review", 
                     provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """Code analysis and review"""
        prompts = {
            "review": "Review this code for bugs, security issues, and improvements:",
            "explain": "Explain what this code does in detail:",
            "optimize": "Optimize this code for better performance:",
            "document": "Add comprehensive documentation to this code:"
        }
        
        messages = [
            {"role": "system", "content": "You are a senior software engineer."},
            {"role": "user", "content": f"{prompts.get(task, prompts['review'])}\n\n```{code}\n```"}
        ]
        
        return self.chat(messages, provider, model, temperature=0.3)


# Singleton instance
_ai_provider = None

def get_ai_provider(config_path: str = "config/.env") -> AIProvider:
    """Get or create AI provider singleton"""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = AIProvider(config_path)
    return _ai_provider


if __name__ == "__main__":
    import sys
    
    # Test the provider
    provider = get_ai_provider()
    
    print("Available AI Providers:")
    print("-" * 40)
    for name in provider.list_available_providers():
        config = provider.provider_configs[name]
        print(f"  ✅ {name}")
        print(f"     Default model: {config['default_model']}")
        if 'models' in config:
            print(f"     Available models: {', '.join(config['models'][:3])}")
        print()
    
    if len(sys.argv) > 1:
        # Test chat with specific provider
        test_provider = sys.argv[1]
        test_message = sys.argv[2] if len(sys.argv) > 2 else "Hello!"
        
        print(f"\nTesting {test_provider} with: '{test_message}'")
        print("-" * 40)
        
        try:
            response = provider.chat(
                [{"role": "user", "content": test_message}],
                provider=test_provider
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
