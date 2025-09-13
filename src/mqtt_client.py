#!/usr/bin/env python3
"""
Simple MQTT publisher utility for YTLite
Reads connection from env: MQTT_HOST, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_BASE_TOPIC
Publishes JSON payloads under topic: {base}/events/{project or 'global'}/{event}
"""
from __future__ import annotations
import os
import json
import time
import platform
from typing import Any, Optional, Sequence
from logging_setup import get_logger

logger = get_logger("mqtt")

try:
    import paho.mqtt.client as mqtt  # type: ignore
    _MQTT_AVAILABLE = True
except Exception as e:
    _MQTT_AVAILABLE = False
    logger.warning(f"paho-mqtt not available: {e}. MQTT notifications disabled.")


def _connect_client() -> Optional["mqtt.Client"]:
    if not _MQTT_AVAILABLE:
        return None
    host = os.getenv("MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    client_id = os.getenv("MQTT_CLIENT_ID", "ytlite-webgui")

    try:
        client = mqtt.Client(client_id=client_id, clean_session=True)
        if username:
            try:
                client.username_pw_set(username, password)
            except Exception:
                pass
        client.connect(host, port, keepalive=10)
        return client
    except Exception as e:
        logger.warning(f"MQTT connect failed: {e}")
        return None


def publish_mqtt_event(event: str,
                       level: str = "info",
                       project: Optional[str] = None,
                       details: Optional[dict[str, Any]] = None,
                       tags: Optional[Sequence[str]] = None) -> bool:
    """Publish a structured event over MQTT. Returns True if published, else False.
    Adds metadata: ts, host, pid, app, phase, threshold_db, tags.
    """
    base = os.getenv("MQTT_BASE_TOPIC", "ytlite")
    topic = f"{base}/events/{project or 'global'}/{event}"
    # infer phase from event name
    phase = 'postgen' if event.startswith('postgen_') else ('preplay' if event.startswith('preplay_') else None)
    # include optional threshold if defined
    threshold_db = os.getenv("MEDIA_SILENCE_DB")
    payload = {
        "event": event,
        "level": level,
        "project": project,
        "details": details or {},
        "ts": time.time(),
        "host": platform.node(),
        "pid": os.getpid(),
        "app": "ytlite",
        "phase": phase,
        "threshold_db": float(threshold_db) if threshold_db else None,
        "tags": list(tags) if tags else None,
    }
    client = _connect_client()
    if client is None:
        return False
    try:
        client.loop_start()
        client.publish(topic, json.dumps(payload), qos=0, retain=False)
        client.loop_stop()
        client.disconnect()
        logger.info(f"MQTT published: {topic}", extra={"payload": payload})
        return True
    except Exception as e:
        logger.warning(f"MQTT publish failed to {topic}: {e}")
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
        return False
