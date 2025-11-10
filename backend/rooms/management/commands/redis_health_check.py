"""
Django management command to check Redis health
Usage: python manage.py redis_health_check
"""
from django.core.management.base import BaseCommand
from rooms.redis_health import log_redis_health


class Command(BaseCommand):
    help = 'Check Redis connection health and log statistics'

    def handle(self, *args, **options):
        self.stdout.write('Checking Redis health...')
        
        health_status = log_redis_health()
        
        if health_status['overall_healthy']:
            self.stdout.write(self.style.SUCCESS('✅ Redis is healthy'))
        else:
            self.stdout.write(self.style.ERROR('❌ Redis health check failed'))
            
        self.stdout.write(f"Connection: {'✅' if health_status['connection_healthy'] else '❌'}")
        self.stdout.write(f"Channels: {'✅' if health_status['channels_healthy'] else '❌'}")
        
        if health_status['stats']:
            stats = health_status['stats']
            self.stdout.write('\nRedis Statistics:')
            self.stdout.write(f"  Version: {stats.get('redis_version', 'N/A')}")
            self.stdout.write(f"  Uptime: {stats.get('uptime_in_seconds', 0)} seconds")
            self.stdout.write(f"  Connected clients: {stats.get('connected_clients', 0)}")
            self.stdout.write(f"  Memory usage: {stats.get('used_memory_human', 'N/A')}")
            self.stdout.write(f"  Commands processed: {stats.get('total_commands_processed', 0)}")
            self.stdout.write(f"  Cache hits: {stats.get('keyspace_hits', 0)}")
            self.stdout.write(f"  Cache misses: {stats.get('keyspace_misses', 0)}")
        
        self.stdout.write('\nCheck logs/redis.log for detailed Redis operation logs.')