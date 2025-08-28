import redis
import json

class LeadSessionService:
    def __init__(self):
        # Connect to Redis Cloud server
        self.redis_client = redis.Redis(
            host='redis-10661.c17.us-east-1-4.ec2.redns.redis-cloud.com',
            port=10661,
            decode_responses=True,
            username="default",
            password="RKWH5tuWOhrxTsrAsJucYSCuUjdBXpPa"
        )
    def clear_messages(self, contact_number: str):
        """Clear all messages for a given contact number"""
        key = f"contact:{contact_number}:messages"
        self.redis_client.delete(key)
    
    def add_message(self, contact_number: str, message: dict):
        """Add a message to the contact's history"""
        key = f"contact:{contact_number}:messages"
        self.redis_client.rpush(key, json.dumps(message))
    
    def get_messages(self, contact_number: str) -> list:
        """Get all messages for a given contact number"""
        key = f"contact:{contact_number}:messages"
        messages = self.redis_client.lrange(key, 0, -1)
        return [json.loads(msg) for msg in messages]
    
    def clear_messages(self, contact_number: str):
        """Clear all messages for a given contact number"""
        key = f"contact:{contact_number}:messages"
        self.redis_client.delete(key)