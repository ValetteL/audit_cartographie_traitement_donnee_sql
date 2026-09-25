"""Expose CPU/mémoire par conteneur via l'API Docker (docker.sock), en
remplacement de cAdvisor : sous Docker Desktop (Windows/Mac), les conteneurs
tournent dans une VM cachée et /var/lib/docker monté depuis l'hôte ne
correspond pas au vrai backend de stockage utilisé en interne — cAdvisor ne
peut alors identifier la couche overlayfs d'aucun conteneur et abandonne son
suivi ("failed to identify the read-write layer ID"). L'API Docker (docker.sock)
est l'interface stable exposée par Docker Desktop dans tous les cas, sans
dépendre du driver de stockage ni nécessiter de conteneur privilégié.
"""
import os
import time

import docker
from prometheus_client import Gauge, start_http_server

METRICS_PORT = int(os.environ.get("METRICS_PORT", "8000"))
INTERVAL = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
NAME_PREFIXES = tuple(os.environ.get("NAME_PREFIXES", "tp2_,tp_audit_44_pg").split(","))

CPU_SECONDS = Gauge(
    "docker_container_cpu_seconds_total",
    "Temps CPU cumulé consommé par le conteneur (secondes)",
    ["container"],
)
MEM_BYTES = Gauge(
    "docker_container_memory_usage_bytes",
    "Mémoire utilisée par le conteneur (octets)",
    ["container"],
)


def is_relevant(name):
    return name.startswith(NAME_PREFIXES)


def main():
    start_http_server(METRICS_PORT)
    client = docker.from_env()
    print("[docker-stats-exporter] démarré, interrogation de l'API Docker...")

    while True:
        for container in client.containers.list():
            if not is_relevant(container.name):
                continue
            try:
                stats = container.stats(stream=False)
                cpu_ns = stats["cpu_stats"]["cpu_usage"]["total_usage"]
                mem = stats["memory_stats"].get("usage", 0)
                CPU_SECONDS.labels(container=container.name).set(cpu_ns / 1e9)
                MEM_BYTES.labels(container=container.name).set(mem)
            except Exception as e:
                print(f"[docker-stats-exporter] erreur pour {container.name} : {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
