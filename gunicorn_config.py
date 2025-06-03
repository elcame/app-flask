import multiprocessing
import os

# Configuración básica
bind = "0.0.0.0:" + str(os.getenv("PORT", "5000"))
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120
keepalive = 5

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configuración de worker
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 