redis: /app/redis/start-redis-server.sh
metrics: /usr/local/bin/redis_exporter -redis.addr localhost:6379 -web.listen-address ":9091"
app: gunicorn -b [::]:8080 -w 8 app:app
