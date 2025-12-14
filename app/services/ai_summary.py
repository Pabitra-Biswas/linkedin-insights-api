import logging
import asyncio
from typing import Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AISummaryService:
    def __init__(self):
        self.openai_key: Optional[str] = settings.OPENAI_API_KEY

        if not self.openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not configured; AI summaries will not work.")

    async def generate_page_summary(self, page_data: Dict) -> str:
        """Generate AI-powered insights about the LinkedIn page using OpenAI."""
        
        if not self.openai_key:
            logger.info("Skipping AI summary: OPENAI_API_KEY missing")
            return "AI integration disabled (OPENAI_API_KEY missing)."

        # Construct the Prompt
        prompt = f"""
Analyze this LinkedIn company page and provide comprehensive business insights in about 200-250 words.

Company Information:
- Name: {page_data.get('name', 'N/A')}
- Industry: {page_data.get('industry', 'N/A')}
- Followers: {page_data.get('followers_count', 0):,}
- Company Size: {page_data.get('head_count', 'N/A')}
- Specialities: {', '.join(page_data.get('specialities', []) if page_data.get('specialities') else [])}
- Description: {page_data.get('description', 'N/A')}

Provide a detailed summary covering:
1. Market Positioning
2. Engagement Analysis
3. Brand Strength
4. Target Audience
5. Growth Indicators
6. Strategic Insights
"""

        try:
            # Lazy import to keep startup fast
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                logger.error("❌ langchain-openai library not installed.")
                return "AI unavailable (library missing)."

            # Define the sync function to call OpenAI
            def sync_invoke():
                # We use gpt-4o-mini because it is cheap, fast, and smart
                llm = ChatOpenAI(
                    model="gpt-4o-mini", 
                    api_key=self.openai_key,
                    temperature=0.7
                )
                response = llm.invoke(prompt)
                return response.content

            # Run in a separate thread to not block the server
            summary = await asyncio.to_thread(sync_invoke)
            
            logger.info("✅ AI summary generated for: %s", page_data.get('page_id'))
            return summary.strip()

        except Exception as e:
            logger.exception("❌ OpenAI summary failed: %s", str(e))
            return "AI summary generation failed. Please try again later."