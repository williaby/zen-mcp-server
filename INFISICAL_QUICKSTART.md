# Infisical Quick Start Guide

Get started with Infisical secrets management in 5 minutes.

## 1. Install Dependencies

```bash
# Install Python SDK (already in pyproject.toml)
pip install -e .
# or with uv
uv pip install -e .
```

## 2. Configure Infisical

```bash
# Copy the example config
cp .infisical.json.example .infisical.json

# Edit .infisical.json and add your workspace ID
# Find it at: https://infisical.williamshome.family → Project Settings → Project ID
nano .infisical.json
```

## 3. Set Up Cloudflare Access (Required)

Since Infisical is behind Cloudflare, add Cloudflare tokens to `.env`:

```bash
# Create .env file if it doesn't exist
cp .env.example .env

# Add Cloudflare Access credentials (get from Cloudflare Zero Trust dashboard)
cat >> .env <<EOF
CF_ACCESS_CLIENT_ID=your-cloudflare-client-id
CF_ACCESS_CLIENT_SECRET=your-cloudflare-client-secret
EOF
```

## 4. Set Infisical Authentication

```bash
# Option A: Machine Identity Token (recommended)
export INFISICAL_TOKEN="your-machine-identity-token"

# Option B: Universal Auth
export INFISICAL_CLIENT_ID="your-client-id"
export INFISICAL_CLIENT_SECRET="your-client-secret"
```

## 5. Add Secrets to Infisical

1. Go to <https://infisical.williamshome.family>
2. Navigate to your `zen-mcp-server` project
3. Select the **dev** environment
4. Add at least one API key:
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`
   - `XAI_API_KEY`
   - `DIAL_API_KEY`
   - `OPENROUTER_API_KEY`

## 6. Run the Server

```bash
# Server will automatically load secrets from Infisical
./run-server.sh
```

You should see a log message confirming secrets were loaded:

```text
Loaded X secrets from Infisical https://infisical.williamshome.family
(workspace: abc123, env: dev)
```

## Troubleshooting

### No secrets loaded?

**Check Cloudflare Access tokens FIRST:**

```bash
grep CF_ACCESS .env
# Should show both CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET
```

**Then check Infisical authentication:**

```bash
echo $INFISICAL_TOKEN
# Should output your token (not empty)
```

**Check workspace ID:**

```bash
cat .infisical.json | grep workspaceId
# Should show your actual project ID (not "your-workspace-id-from...")
```

**Enable debug logging:**

```bash
export LOG_LEVEL=DEBUG
./run-server.sh
```

### Using .env fallback

If Infisical is unavailable, the system automatically falls back to `.env`:

```bash
cp .env.example .env
# Edit .env with your API keys
./run-server.sh
```

## Next Steps

- **Full Documentation**: See [docs/INFISICAL_SETUP.md](docs/INFISICAL_SETUP.md)
- **Environment-specific configs**: Set up staging and prod environments
- **CLI Integration**: Install Infisical CLI for advanced features
- **Migration Guide**: Migrate existing `.env` secrets to Infisical

## Self-Hosted Instance Info

- **Primary URL**: `https://infisical.williamshome.family`
- **Alternate**: `http://192.168.1.16:8082`
- **Pre-configured** in `.infisical.json.example`
