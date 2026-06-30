import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

updated = {"qwen": False, "parseai": False}

for n in wf['nodes']:
    # Change 1: node-qwen -> Groq AI
    if n.get('id') == 'node-qwen':
        n['name'] = 'Groq AI'
        n['parameters']['url'] = 'https://api.groq.com/openai/v1/chat/completions'
        n['parameters']['sendHeaders'] = True
        n['parameters']['headerParameters'] = {
            "parameters": [{"name": "Authorization", "value": "Bearer YOUR_GROQ_API_KEY_HERE"}]
        }
        n['parameters']['body'] = "={{ JSON.stringify({ model: 'llama-3.3-70b-versatile', temperature: 0.3, messages: $json.messages }) }}"
        updated['qwen'] = True

    # Change 2: node-parseai -> fix content extraction
    if n.get('id') == 'node-parseai':
        old_line = "const content = aiResp.message?.content || '';"
        new_line = "const content = aiResp.choices?.[0]?.message?.content || '';"
        if old_line in n['parameters']['jsCode']:
            n['parameters']['jsCode'] = n['parameters']['jsCode'].replace(old_line, new_line)
            updated['parseai'] = True

# Also update connections that reference "Qwen AI" by name
for src, targets in wf.get('connections', {}).items():
    for branch in targets.get('main', []):
        for t in branch:
            if t.get('node') == 'Qwen AI':
                t['node'] = 'Groq AI'

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print("node-qwen updated:", updated['qwen'])
print("node-parseai updated:", updated['parseai'])
print("Done.")
