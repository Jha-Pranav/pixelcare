#!/bin/bash
cd "$(dirname "$0")/app/vitals"
uv run live_collector.py
