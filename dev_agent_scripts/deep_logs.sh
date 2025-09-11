#!/bin/bash
echo "[DEEP LOGS] Gathering logs..."
mkdir -p logs
[ -f project.log ] && tail -n 100 project.log > logs/project_tail.log

