#!/usr/bin/env bash
# Downloads the Kokoro voice model used for narration into ./tts (not committed).
set -e
mkdir -p tts && cd tts
curl -sS -L -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
curl -sS -L -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
ls -la
