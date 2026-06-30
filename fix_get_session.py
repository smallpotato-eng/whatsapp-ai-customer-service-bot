import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for node in wf['nodes']:
    if node['id'] == 'univ-get-session':
        node['continueOnFail'] = True
        node['parameters']['options'] = {
            "response": {
                "response": {
                    "alwaysOutputData": True
                }
            }
        }
        print('✅ Get Session fixed')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
