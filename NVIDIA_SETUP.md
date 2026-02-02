# NVIDIA API Setup

Quick setup guide for using NVIDIA API with nanobot.

## 1. Get API Key

1. Go to [build.nvidia.com](https://build.nvidia.com)
2. Sign in with your NVIDIA account
3. Navigate to **API Catalog** → **Zhipu AI** (or other model)
4. Click **"Get API Key"** to generate your key

## 2. Configure nanobot

Copy the example config to your nanobot directory:

```bash
# Linux/macOS
cp config.example.nvidia.json ~/.nanobot/config.json

# Windows (PowerShell)
Copy-Item config.example.nvidia.json $env:USERPROFILE\.nanobot\config.json
```

Or create `~/.nanobot/config.json` manually:

```json
{
  "providers": {
    "nvidia": {
      "api_key": "nvapi-YOUR_KEY_HERE",
      "api_base": "https://integrate.api.nvidia.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "z-ai/glm4.7",
      "max_tokens": 16384,
      "temperature": 1.0
    }
  }
}
```

## 3. Test

```bash
# Test single message
nanobot agent -m "Hello, what is 2+2?"

# Start gateway server
nanobot gateway
```

## Available Models

- `z-ai/glm4.7` (default) - Zhipu GLM 4.7 with thinking mode
- Other models available in NVIDIA API catalog

## Features

- Auto-detection: nanobot automatically uses NVIDIA provider when `nvidia.api_key` is set
- Thinking mode enabled by default for `glm` models
- No additional environment variables needed

## Troubleshooting

**Unicode errors on Windows**: Set console to UTF-8:
```powershell
chcp 65001
```

**API errors**: Verify your API key is active at [build.nvidia.com](https://build.nvidia.com)
