import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for node in wf['nodes']:
    if node['id'] == 'univ-save-user':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone_number: $('Parse AI Response').item.json.phone, role: 'user', content: $('Parse AI Response').item.json.userText }) }}"
        print('✅ Save User Msg fixed')

    if node['id'] == 'univ-save-ai':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone_number: $('Parse AI Response').item.json.phone, role: 'assistant', content: $('Parse AI Response').item.json.replyText }) }}"
        print('✅ Save AI Reply fixed')

    if node['id'] == 'univ-save-session':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone_number: $('Extract Message').item.json.phone, business_type: 'universal', status: 'active' }) }}"
        print('✅ Save Session fixed')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
