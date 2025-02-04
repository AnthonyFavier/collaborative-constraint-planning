KEY="REPLACE_WITH_YOUR_KEY"

with open('set_claude_api_key.sh', 'w') as f:
    f.write("export ANTHROPIC_API_KEY='" + KEY + "'")