"""
Custom Redis channel layer with comprehensive logging
Wraps the default Redis channel layer to log all Redis operations
"""
import logging
import json
import asyncio
from channels_redis.core import RedisChannelLayer
from asgiref.sync import sync_to_async

# Set up Redis logger
redis_logger = logging.getLogger('rooms.redis')


class LoggingRedisChannelLayer(RedisChannelLayer):
    """
    Custom Redis channel layer that logs all operations
    """
    
    async def send(self, channel, message):
        """Log channel sends"""
        redis_logger.info(f"REDIS SEND - Channel: {channel}")
        redis_logger.debug(f"REDIS SEND - Message: {json.dumps(message, default=str)}")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await super().send(channel, message)
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.info(f"REDIS SEND SUCCESS - Channel: {channel}, Duration: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.error(f"REDIS SEND ERROR - Channel: {channel}, Error: {str(e)}, Duration: {duration:.2f}ms")
            raise

    async def receive(self, channels):
        """Log channel receives"""
        redis_logger.debug(f"REDIS RECEIVE - Waiting on channels: {channels}")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await super().receive(channels)
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if result:
                channel, message = result
                redis_logger.info(f"REDIS RECEIVE SUCCESS - Channel: {channel}, Duration: {duration:.2f}ms")
                redis_logger.debug(f"REDIS RECEIVE - Message: {json.dumps(message, default=str)}")
            else:
                redis_logger.debug(f"REDIS RECEIVE TIMEOUT - Duration: {duration:.2f}ms")
                
            return result
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.error(f"REDIS RECEIVE ERROR - Channels: {channels}, Error: {str(e)}, Duration: {duration:.2f}ms")
            raise

    async def group_add(self, group, channel):
        """Log group additions"""
        redis_logger.info(f"REDIS GROUP_ADD - Group: {group}, Channel: {channel}")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await super().group_add(group, channel)
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.info(f"REDIS GROUP_ADD SUCCESS - Group: {group}, Channel: {channel}, Duration: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.error(f"REDIS GROUP_ADD ERROR - Group: {group}, Channel: {channel}, Error: {str(e)}, Duration: {duration:.2f}ms")
            raise

    async def group_discard(self, group, channel):
        """Log group removals"""
        redis_logger.info(f"REDIS GROUP_DISCARD - Group: {group}, Channel: {channel}")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await super().group_discard(group, channel)
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.info(f"REDIS GROUP_DISCARD SUCCESS - Group: {group}, Channel: {channel}, Duration: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.error(f"REDIS GROUP_DISCARD ERROR - Group: {group}, Channel: {channel}, Error: {str(e)}, Duration: {duration:.2f}ms")
            raise

    async def group_send(self, group, message):
        """Log group sends"""
        redis_logger.info(f"REDIS GROUP_SEND - Group: {group}")
        redis_logger.debug(f"REDIS GROUP_SEND - Message: {json.dumps(message, default=str)}")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await super().group_send(group, message)
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.info(f"REDIS GROUP_SEND SUCCESS - Group: {group}, Duration: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.error(f"REDIS GROUP_SEND ERROR - Group: {group}, Error: {str(e)}, Duration: {duration:.2f}ms")
            raise

    async def new_channel(self, prefix="specific"):
        """Log new channel creation"""
        result = await super().new_channel(prefix)
        redis_logger.info(f"REDIS NEW_CHANNEL - Channel: {result}, Prefix: {prefix}")
        return result

    async def flush(self):
        """Log Redis flush operations"""
        redis_logger.warning("REDIS FLUSH - Clearing all Redis data")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await super().flush()
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.warning(f"REDIS FLUSH SUCCESS - Duration: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            redis_logger.error(f"REDIS FLUSH ERROR - Error: {str(e)}, Duration: {duration:.2f}ms")
            raise