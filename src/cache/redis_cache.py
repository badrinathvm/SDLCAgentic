import redis
import json
from typing import Optional

from src.state.sdlc_state import CustomEncoder, SDLCState

# Initialize RedisCheckpoint
redis_client = redis.Redis(
    host='localhost',  # Replace with your Redis host
    port=6379,         # Replace with your Redis port
    db=0               # Replace with your Redis database number
)

def save_state_to_redis(task_id: str, state: SDLCState):
    """Save the state to Redis."""
    state = json.dumps(state, cls=CustomEncoder)
    redis_client.set(task_id, state)

    # Set expiration for 24 hours
    redis_client.expire(task_id, 86400)

def get_state_from_redis(task_id: str) -> Optional[SDLCState]:
    """ Retrieves the statwe from redis """
    state_json = redis_client.get(task_id)
    if not state_json:
        return None
    
    state_dict = json.loads(state_json)[0]
    return SDLCState(**state_dict)

def delete_from_redis(task_id: str):
    """ Delete from redis """
    redis_client.delete(task_id)

def flush_redis_cache():
    """ Flushes the whole cache"""

    # Clear all keys in all databases
    redis_client.flushall()

    print("--- Redis cache cleared ---")
