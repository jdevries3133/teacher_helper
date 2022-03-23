#!/bin/sh

# terraform programs must output valid JSON

echo '{"output": "'"$(git describe --tags)"'"}'
