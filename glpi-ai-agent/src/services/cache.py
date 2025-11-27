import time
import logging
from typing import Dict, List, Tuple, Optional
from src.config.settings import Config

logger = logging.getLogger(__name__)

class CategoryCache:
    """
    In-memory cache for GLPI categories with TTL (Time To Live).
    Reduces redundant API calls to GLPI for category lookups.
    """
    
    def __init__(self):
        self.categories: List[Dict] = []
        self.cat_map: Dict[str, int] = {}  # completename -> id
        self.leaf_map: Dict[str, int] = {}  # name -> id
        self.last_updated: float = 0
        self.ttl_seconds: int = Config.CATEGORY_CACHE_TTL_SECONDS
        
    def is_expired(self) -> bool:
        """Check if cache has expired based on TTL."""
        if not self.categories:
            return True
        
        elapsed = time.time() - self.last_updated
        return elapsed > self.ttl_seconds
    
    def update(self, categories: List[Dict]) -> None:
        """
        Update cache with fresh category data from GLPI.
        
        Args:
            categories: List of category dictionaries from GLPI API
        """
        self.categories = categories
        
        # Build completename -> id map (preferred)
        self.cat_map = {
            c.get('completename'): c.get('id') 
            for c in categories 
            if c.get('completename') and c.get('id')
        }
        
        # Build leaf name -> id map (fallback)
        self.leaf_map = {
            c.get('name'): c.get('id') 
            for c in categories 
            if c.get('name') and c.get('id')
        }
        
        self.last_updated = time.time()
        logger.info(f"🔄 Category cache updated: {len(self.cat_map)} categories loaded")
    
    def get_maps(self) -> Tuple[Dict[str, int], Dict[str, int], List[str]]:
        """
        Get category maps and names list.
        
        Returns:
            Tuple of (cat_map, leaf_map, cat_names)
            - cat_map: {completename: id}
            - leaf_map: {name: id}
            - cat_names: list of completename strings
        """
        cat_names = list(self.cat_map.keys())
        return self.cat_map, self.leaf_map, cat_names
    
    def get_cache_info(self) -> Dict:
        """Get cache statistics for debugging."""
        elapsed = time.time() - self.last_updated if self.last_updated > 0 else 0
        return {
            "total_categories": len(self.categories),
            "cache_age_seconds": int(elapsed),
            "ttl_seconds": self.ttl_seconds,
            "is_expired": self.is_expired()
        }
