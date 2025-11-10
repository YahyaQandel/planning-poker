from django.apps import AppConfig
import logging


class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rooms'
    
    def ready(self):
        import rooms.signals
        
        # Initialize Redis health monitoring
        try:
            from .redis_health import log_redis_health
            logger = logging.getLogger('rooms.redis')
            logger.info("REDIS INIT - Initializing Redis health monitoring")
            log_redis_health()
        except Exception as e:
            logger = logging.getLogger('rooms.redis')
            logger.error(f"REDIS INIT - Failed to initialize Redis health monitoring: {str(e)}")
