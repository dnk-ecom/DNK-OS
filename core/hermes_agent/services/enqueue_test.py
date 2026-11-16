import redis; r = redis.Redis(); r.lpush("hermes:queue", "test_job")
