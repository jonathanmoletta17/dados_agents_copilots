import traceback
import logging
from src.config.settings import Config
from src.clients.glpi import GLPIClient
from src.clients.ollama import LocalAIClient
from src.services.cache import CategoryCache

logger = logging.getLogger(__name__)

# Global category cache instance
_category_cache = CategoryCache()

async def handle_ticket_update(ticket_id: int, context: str):
    try:
        logger.info(f"🚀 [AI Service] Starting processing for Ticket #{ticket_id} (Context: {context})")
        
        creds = Config.get_credentials(context)
        if not creds['url'] or not creds['app_token'] or not creds['user_token']:
            logger.error(f"Missing credentials for context '{context}'. Skipping.")
            return

        client = GLPIClient(
            base_url=creds['url'],
            app_token=creds['app_token'],
            user_token=creds['user_token']
        )
        
        # 1. Fetch Ticket
        try:
            ticket = client.make_request(f"Ticket/{ticket_id}")
        except Exception as e:
            logger.error(f"Failed to fetch ticket {ticket_id}: {e}")
            return

        title = ticket.get('name', '')
        description = ticket.get('content', '')
        current_cat_id = ticket.get('itilcategories_id', 0)
        
        # 2. Fetch Categories (with cache)
        # Check if cache is valid, refresh if expired
        if _category_cache.is_expired():
            logger.info("⏰ Category cache expired or empty, fetching from GLPI...")
            categories = client.get_all_pages("ITILCategory")
            _category_cache.update(categories)
        else:
            cache_info = _category_cache.get_cache_info()
            logger.debug(f"📦 Using cached categories (age: {cache_info['cache_age_seconds']}s, total: {cache_info['total_categories']})")
        
        # Get maps from cache
        cat_map, leaf_map, cat_names = _category_cache.get_maps()
        
        if not cat_names:
            logger.warning("No categories found in GLPI.")
            return

        # 3. Call AI
        ai = LocalAIClient()
        suggestion = ai.suggest_category(title, description, cat_names)
        
        if suggestion:
            suggested_id = cat_map.get(suggestion)
            
            # Fallback to leaf name if full name match fails
            if not suggested_id:
                suggested_id = leaf_map.get(suggestion)
            
            if suggested_id:
                # Check if update is needed
                # current_cat_id might be int or str, ensure comparison is safe
                if int(suggested_id) != int(current_cat_id):
                    logger.info(f"✨ Updating Ticket #{ticket_id}: Category {current_cat_id} -> {suggested_id} ({suggestion})")
                    client.update_ticket(ticket_id, {"itilcategories_id": suggested_id})
                else:
                    logger.info(f"ℹ️ No update needed for Ticket #{ticket_id}. AI suggested current category: {suggestion}")
            else:
                logger.warning(f"⚠️ AI suggested '{suggestion}' but ID could not be resolved in category map.")
        else:
            logger.warning(f"⚠️ AI did not return a valid category for Ticket #{ticket_id}")

    except Exception as e:
        logger.error(f"❌ Error in AI service for Ticket #{ticket_id}: {e}")
        logger.error(traceback.format_exc())
