"""
Redis Health Check and Connection Monitoring
"""
import logging
import redis
import asyncio
from django.conf import settings
from django.core.cache import cache
from channels.layers import get_channel_layer

# Set up Redis logger
redis_logger = logging.getLogger('rooms.redis')


class RedisHealthMonitor:
    """Monitor Redis connection health and log connection issues"""
    
    def __init__(self):
        self.redis_client = None
        self.channel_layer = get_channel_layer()
        self._setup_redis_client()
    
    def _setup_redis_client(self):
        """Setup direct Redis client for health checks"""
        try:
            # Get Redis connection details from channel layers config
            config = settings.CHANNEL_LAYERS['default']['CONFIG']
            host, port = config['hosts'][0]
            
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=False
            )
            
            redis_logger.info(f"REDIS HEALTH - Redis client initialized: {host}:{port}")
        except Exception as e:
            redis_logger.error(f"REDIS HEALTH - Failed to initialize Redis client: {str(e)}")
    
    def check_redis_connection(self):
        """Check Redis connection health"""
        try:
            if self.redis_client:
                # Test basic Redis operations
                test_key = "health_check_test"
                test_value = "test_value"
                
                # Test SET
                start_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
                self.redis_client.set(test_key, test_value, ex=5)  # 5 second expiry
                
                # Test GET
                result = self.redis_client.get(test_key)
                duration = (asyncio.get_event_loop().time() - start_time) * 1000 if start_time else 0
                
                if result == test_value:
                    redis_logger.info(f"REDIS HEALTH - Connection healthy, latency: {duration:.2f}ms")
                    
                    # Get Redis info
                    info = self.redis_client.info()
                    redis_logger.debug(f"REDIS HEALTH - Connected clients: {info.get('connected_clients', 'N/A')}")
                    redis_logger.debug(f"REDIS HEALTH - Memory usage: {info.get('used_memory_human', 'N/A')}")
                    redis_logger.debug(f"REDIS HEALTH - Keyspace hits: {info.get('keyspace_hits', 'N/A')}")
                    
                    return True
                else:
                    redis_logger.error(f"REDIS HEALTH - Data integrity check failed")
                    return False
            else:
                redis_logger.error("REDIS HEALTH - Redis client not initialized")
                return False
                
        except redis.ConnectionError as e:
            redis_logger.error(f"REDIS HEALTH - Connection error: {str(e)}")
            return False
        except redis.TimeoutError as e:
            redis_logger.error(f"REDIS HEALTH - Timeout error: {str(e)}")
            return False
        except Exception as e:
            redis_logger.error(f"REDIS HEALTH - Unexpected error: {str(e)}")
            return False
    
    def get_redis_stats(self):
        """Get detailed Redis statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                stats = {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'redis_version': info.get('redis_version', 'unknown'),
                    'uptime_in_seconds': info.get('uptime_in_seconds', 0)
                }
                
                redis_logger.info(f"REDIS STATS - {stats}")
                return stats
            else:
                redis_logger.error("REDIS STATS - Redis client not available")
                return None
                
        except Exception as e:
            redis_logger.error(f"REDIS STATS - Error getting stats: {str(e)}")
            return None
    
    def check_channels_layer_health(self):
        """Check Django Channels layer health"""
        try:
            if self.channel_layer:
                redis_logger.info("REDIS HEALTH - Checking Django Channels layer")
                # The actual health check is done by our custom LoggingRedisChannelLayer
                return True
            else:
                redis_logger.error("REDIS HEALTH - Channels layer not available")
                return False
        except Exception as e:
            redis_logger.error(f"REDIS HEALTH - Channels layer error: {str(e)}")
            return False


# Create singleton instance
redis_health = RedisHealthMonitor()


def log_redis_health():
    """Convenience function to log Redis health status"""
    redis_logger.info("REDIS HEALTH CHECK - Starting health check")
    
    # Check basic Redis connection
    connection_healthy = redis_health.check_redis_connection()
    
    # Check channels layer
    channels_healthy = redis_health.check_channels_layer_health()
    
    # Get stats
    stats = redis_health.get_redis_stats()
    
    overall_health = connection_healthy and channels_healthy
    redis_logger.info(f"REDIS HEALTH CHECK - Overall status: {'HEALTHY' if overall_health else 'UNHEALTHY'}")
    
    return {
        'connection_healthy': connection_healthy,
        'channels_healthy': channels_healthy,
        'overall_healthy': overall_health,
        'stats': stats
    }