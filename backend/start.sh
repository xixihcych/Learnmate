#!/bin/bash
echo "Starting LearnMate Backend..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000






