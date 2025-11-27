import requests
import logging
from typing import List, Optional
from src.config.settings import Config

logger = logging.getLogger(__name__)

class LocalAIClient:
    def __init__(self):
        self.api_url = Config.AI_SERVICE_URL
        self.model = Config.AI_MODEL_NAME
        self.threshold = Config.AI_CONFIDENCE_THRESHOLD

    def suggest_category(self, title: str, description: str, categories: List[str]) -> Optional[str]:
        """
        Sends ticket data to local AI model and returns the suggested category.
        """
        if not self.api_url:
            logger.warning("AI_SERVICE_URL not configured. Skipping AI processing.")
            return None

        prompt = self._construct_prompt(title, description, categories)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2  # Low temperature for deterministic output
            }
        }

        try:
            logger.info(f"Sending request to AI Model ({self.model}) at {self.api_url}")
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            suggestion = result.get("response", "").strip()
            
            logger.info(f"AI Suggestion: '{suggestion}'")
            
            # Basic validation: check if suggestion is in the list of categories
            # We do a case-insensitive check
            categories_lower = {c.lower(): c for c in categories}
            
            if suggestion.lower() in categories_lower:
                return categories_lower[suggestion.lower()]
            else:
                # Try to find a partial match or handle "No category"
                # For now, if it doesn't match exactly (case-insensitive), we reject it to be safe
                logger.warning(f"AI suggested '{suggestion}' which is not in the available categories list.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with AI service: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in AI processing: {e}")
            return None

    def _construct_prompt(self, title: str, description: str, categories: List[str]) -> str:
        categories_str = "\n".join([f"- {c}" for c in categories])
        
        return f"""You are an IT Service Desk categorization specialist. Your ONLY task is to select the most appropriate category from the list below.

TICKET INFORMATION:
Title: {title}
Description: {description}

AVAILABLE CATEGORIES (choose ONE from this list):
{categories_str}

STRICT RULES:
1. You MUST select EXACTLY ONE category from the list above.
2. Copy the category name EXACTLY as it appears in the list.
3. DO NOT create new category names or variations.
4. DO NOT include explanations, justifications, or extra text.
5. If multiple categories could apply, choose the most specific one.
6. If none fit well, reply with "Unknown".

Your response (category name only):"""
