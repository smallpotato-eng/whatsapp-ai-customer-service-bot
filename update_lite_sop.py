import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Replace Load SOP (HTTP GET Google Sheets) with Read Binary File
# Then replace Parse SOP (CSV parser) with plain text reader

new_load_sop = {
    "id": "univ-load-sop",
    "name": "Load SOP",
    "type": "n8n-nodes-base.readBinaryFile",
    "typeVersion": 1,
    "position": [900, 300],
    "parameters": {
        "filePath": "C:/cs-ai/sop.txt"
    }
}

new_parse_sop_code = """// Read plain text SOP file and parse key=value lines
const binaryData = $input.first().binary?.data;
let raw = '';

if (binaryData) {
  // Decode base64 binary to string
  raw = Buffer.from(binaryData.data, 'base64').toString('utf-8');
} else {
  raw = $input.first().json?.data || '';
}

const sop = {};
const lines = raw.split('\\n');

for (const line of lines) {
  const eqIdx = line.indexOf('=');
  if (eqIdx === -1) continue;
  const key = line.substring(0, eqIdx).trim().toLowerCase().replace(/\\s+/g, '_');
  const value = line.substring(eqIdx + 1).trim();
  if (key && value) sop[key] = value;
}

// sop_content: everything after the [SOP] marker (multi-line)
const sopMarker = raw.indexOf('[SOP]');
if (sopMarker !== -1) {
  sop['sop_content'] = raw.substring(sopMarker + 5).trim();
}

return [{ json: sop }];"""

for n in wf['nodes']:
    if n['id'] == 'univ-load-sop':
        n.update(new_load_sop)
        print('Load SOP updated to Read Binary File')

    if n['id'] == 'univ-parse-sop':
        n['parameters']['jsCode'] = new_parse_sop_code
        print('Parse SOP updated to plain text parser')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
