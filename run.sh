#!/bin/bash

uv run python -m bin.consumer &
uv run python -m bin.api &

wait