sysctl vm.overcommit_memory=1
sysctl net.core.somaxconn=1024
redis-server --requirepass $CACHE_REDIS_PASSWORD --dir $(mktemp -d)
