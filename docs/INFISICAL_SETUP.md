# Infisical Integration Guide

This guide explains how to set up and use Infisical for centralized secrets
management with the Zen MCP Server.

## Overview

The Zen MCP Server supports **three methods** for secrets management,
with automatic fallback:

1. **Infisical Python SDK** (Recommended) - Direct API integration
2. **Infisical CLI** - Command-line tool integration
3. **`.env` file** - Traditional file-based secrets (fallback)

The system automatically detects and uses the best available method.

## Benefits of Infisical

- ✅ **Centralized secrets management** across all your projects
- ✅ **Environment-based configuration** (dev/staging/prod)
- ✅ **Team collaboration** with access controls
- ✅ **Secret rotation** and audit logging
- ✅ **Git branch-based environment detection**
- ✅ **Automatic fallback** to `.env` if Infisical unavailable

## Prerequisites

1. **Infisical Account**: Access your self-hosted instance at:
   - **Primary URL**: `https://infisical.williamshome.family`
   - **Alternate**: `http://192.168.1.16:8082`
2. **Create a Project**: Create a new project for `zen-mcp-server`
3. **Configure Environments**: Set up `dev`, `staging`, and `prod` environments

## Installation

### Option 1: Python SDK (Recommended)

The SDK is already included in `pyproject.toml`:

```bash
# Install dependencies
pip install -e .
# or with uv
uv pip install -e .
```

### Option 2: Infisical CLI

Install the CLI for additional features:

```bash
# macOS
brew install infisical/get-cli/infisical

# Linux
curl -1sLf \
  'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' \
  | sudo -E bash
sudo apt-get update && sudo apt-get install -y infisical

# Windows
scoop bucket add infisical https://github.com/Infisical/scoop-infisical.git
scoop install infisical
```

## Configuration

### Step 1: Configure `.infisical.json`

Update the workspace ID in [.infisical.json](../.infisical.json):

```json
{
  "workspaceId": "your-workspace-id-here",
  "siteUrl": "https://infisical.williamshome.family",
  "defaultEnvironment": "dev",
  "gitBranchToEnvironmentMapping": {
    "main": "prod",
    "staging": "staging",
    "dev": "dev",
    "develop": "dev"
  }
}
```

**Find your Workspace ID:**

1. Go to your Infisical instance at `https://infisical.williamshome.family`
2. Navigate to your `zen-mcp-server` project
3. Click **Settings** → **Project ID**
4. Copy the Project ID (this is your workspace ID)

**Note**: The `siteUrl` is pre-configured for your self-hosted instance.
If using the IP address instead, change it to `http://192.168.1.16:8082`

### Step 2: Cloudflare Access Authentication (Required for Self-Hosted)

Since your Infisical instance is behind Cloudflare Access, you need to set up
Cloudflare service tokens first:

1. Go to Cloudflare Zero Trust Dashboard
2. Navigate to **Access** → **Service Auth** → **Service Tokens**
3. Create a new service token
4. Add the credentials to your `.env` file:

```bash
CF_ACCESS_CLIENT_ID=your-cloudflare-client-id
CF_ACCESS_CLIENT_SECRET=your-cloudflare-client-secret
```

**Important**: These must be set in `.env` (not just environment variables) so
they're available when the server starts.

### Step 3: Infisical Authentication

Choose **one** Infisical authentication method:

#### Method A: Machine Identity (Recommended for CI/CD)

1. In Infisical, go to **Project Settings** → **Machine Identities**
2. Create a new machine identity
3. Generate a token
4. Set the environment variable:

```bash
export INFISICAL_TOKEN="your-machine-identity-token"
```

#### Method B: Universal Auth (For Development)

1. In Infisical, go to **Project Settings** → **Access Control** → **Service Tokens**
2. Create Universal Auth credentials
3. Set the environment variables:

```bash
export INFISICAL_CLIENT_ID="your-client-id"
export INFISICAL_CLIENT_SECRET="your-client-secret"
```

### Step 4: Add Secrets to Infisical

In the Infisical dashboard, add your secrets for each environment:

**Required Secrets (add at least one API key):**

- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `XAI_API_KEY`
- `DIAL_API_KEY`
- `OPENROUTER_API_KEY`

**Optional Secrets:**

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `CUSTOM_API_URL`
- `CUSTOM_API_KEY`
- `DEFAULT_MODEL`
- `DEFAULT_THINKING_MODE_THINKDEEP`
- `LOG_LEVEL`
- `DISABLED_TOOLS`

## Usage

### Important: Cloudflare Access Setup

Before using Infisical, ensure Cloudflare Access tokens are in your `.env` file:

```bash
# Required for accessing infisical.williamshome.family
CF_ACCESS_CLIENT_ID=your-cloudflare-client-id
CF_ACCESS_CLIENT_SECRET=your-cloudflare-client-secret
```

**Why `.env` and not environment variables?**
- The Infisical integration loads on server startup before env vars are processed
- `.env` file ensures tokens are available early in the boot process
- This allows seamless authentication through Cloudflare's gateway

### Automatic Loading (Default)

The server automatically loads secrets from Infisical on startup:

```bash
./run-server.sh
```

The loading priority is:

1. **Infisical SDK** (if `INFISICAL_TOKEN` or `INFISICAL_CLIENT_ID`/`SECRET` set)
2. **Infisical CLI** (if `infisical` command available and project configured)
3. **`.env` file** (traditional fallback)

### Environment Detection

The system automatically detects the environment based on:

1. **Explicit `INFISICAL_ENV` or `ENV` variable**:

   ```bash
   export INFISICAL_ENV=prod
   ./run-server.sh
   ```

2. **Git branch mapping** (from `.infisical.json`):

   ```bash
   git checkout main     # Uses 'prod' environment
   git checkout staging  # Uses 'staging' environment
   git checkout dev      # Uses 'dev' environment
   ```

3. **Default**: Falls back to `dev` environment

### Manual CLI Usage

If you prefer using the CLI directly:

```bash
# Login to Infisical
infisical login

# Link to your project
infisical init

# Run server with Infisical secrets
infisical run -- ./run-server.sh

# Or export secrets to shell
infisical export --env=dev --format=dotenv > .env
```

### Verify Secrets Loading

Enable debug logging to see which secrets are loaded:

```bash
export LOG_LEVEL=DEBUG
./run-server.sh
```

You should see log messages like:

```text
Loaded 8 secrets from Infisical (workspace: abc123, env: dev)
```

## Environment-Specific Configuration

### Development (dev)

```bash
# Use development API keys and settings
git checkout dev
./run-server.sh
```

### Staging

```bash
# Use staging environment
git checkout staging
./run-server.sh
```

### Production

```bash
# Use production API keys
git checkout main
export INFISICAL_ENV=prod
./run-server.sh
```

## Troubleshooting

### No secrets loaded from Infisical

**Check Cloudflare Access tokens first:**

```bash
# Verify Cloudflare tokens are in .env
grep CF_ACCESS .env
# Should show:
# CF_ACCESS_CLIENT_ID=xxx
# CF_ACCESS_CLIENT_SECRET=xxx
```

**Check Infisical authentication:**

```bash
# Verify Infisical token is set
echo $INFISICAL_TOKEN
# or
echo $INFISICAL_CLIENT_ID
echo $INFISICAL_CLIENT_SECRET
```

**Check workspace ID:**

```bash
cat .infisical.json | grep workspaceId
```

**Enable debug logging:**

```bash
export LOG_LEVEL=DEBUG
./run-server.sh
```

### CLI not working

**Check CLI installation:**

```bash
infisical --version
```

**Login to Infisical:**

```bash
infisical login
```

**Initialize project:**

```bash
infisical init
```

### Fallback to `.env` file

If Infisical is unavailable, the system automatically falls back to `.env`:

```bash
cp .env.example .env
# Edit .env with your API keys
./run-server.sh
```

## Migration from `.env`

To migrate your existing `.env` configuration to Infisical:

### Step 1: Export current secrets

```bash
# View your current .env file
cat .env
```

### Step 2: Add secrets to Infisical

For each secret in `.env`:

1. Go to Infisical dashboard
2. Select the environment (dev/staging/prod)
3. Click **Add Secret**
4. Enter the key and value
5. Save

### Step 3: Test Infisical loading

```bash
# Rename .env to disable fallback (optional)
mv .env .env.backup

# Run server with Infisical
export INFISICAL_TOKEN="your-token"
./run-server.sh
```

### Step 4: Verify functionality

```bash
# Check that the server starts without errors
# Test a few MCP tools to ensure API keys work
```

## Security Best Practices

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use machine identities for automation** - More secure than service tokens
3. **Rotate secrets regularly** - Use Infisical's rotation features
4. **Use environment-specific secrets** - Different keys for dev/staging/prod
5. **Enable audit logging** - Track who accessed secrets
6. **Use access controls** - Limit who can view/edit production secrets

## Advanced Configuration

### Custom Secret Path

By default, secrets are loaded from `/`. To use a custom path:

```python
from utils.infisical import load_secrets_from_infisical

secrets = load_secrets_from_infisical(path="/zen-mcp-server")
```

### Force CLI over SDK

```python
from utils.infisical import load_secrets_from_infisical

secrets = load_secrets_from_infisical(prefer_cli=True)
```

### Disable Infisical

To temporarily disable Infisical and use `.env` only:

```python
from utils.env import reload_env

reload_env(use_infisical=False)
```

## References

- [Infisical Documentation](https://infisical.com/docs)
- [Infisical Python SDK](https://infisical.com/docs/sdks/languages/python)
- [Infisical CLI Guide](https://infisical.com/docs/cli/overview)
- [Zen MCP Server Environment Configuration](../.env.example)
