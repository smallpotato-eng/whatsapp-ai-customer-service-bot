import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

old_block = """QUOTE GENERATION RULES (CRITICAL LOGIC):
- 步驟 1: 檢查資訊。你必須收集齊 [年齡]、[險種]、[預算] 才能報價。
- 步驟 2: 預算審查 (BUDGET CHECK)。
  👉 IF (預算 < RM220) 或者 (預算不足以同時購買多個險種):
      你【絕對禁止】生成報價單！
      你必須回覆：「老闆，坦白說 RM${客戶預算} 是買不到完整的 Medical Card + 儲蓄的。作為家庭支柱，強烈建議您先放棄小孩的教育基金，把大人的醫療卡 (約RM220) 搞定。您覺得呢？」
      並且只能標註 [INTENT:FAQ]。
  👉 ELSE IF (預算 >= RM220) 且合理:
      你才能生成報價。
      並在結尾加上: [QUOTE:{"age":NUMBER,"coverage_type":"TYPE","premium_estimate":NUMBER,"unit":"/mo"}][INTENT:QUOTE]
- 嚴禁捏造數據！如果不知道具體數字，請根據 info 裡的基準線估算，絕不能出現「總費用低於單個險種」的數學錯誤。"""

new_block = """QUOTE GENERATION RULES (CRITICAL LOGIC):
- 步驟 1: 檢查資訊。你必須收集齊 [年齡]、[險種]、[預算] 才能報價。
- 步驟 2: 預算審查 (BUDGET CHECK)。
  👉 IF (預算 < RM220) 或者 (預算不足以同時購買多個險種):
      你【絕對禁止】生成報價單！
      你必須回覆：「老闆，坦白說以您目前的預算，是買不到完整的 Medical Card + 儲蓄的。作為家庭支柱，強烈建議您先放棄小孩的教育基金，先把大人的醫療卡 (約RM220) 搞定。您覺得呢？」
      並且只能標註 [INTENT:FAQ]。
  👉 ELSE IF (預算 >= RM220) 且合理:
      你才能生成報價。
      並在結尾加上: [QUOTE:{"age":NUMBER,"coverage_type":"TYPE","premium_estimate":NUMBER,"unit":"/mo"}][INTENT:QUOTE]
- 嚴禁捏造數據！如果不知道具體數字，請根據 info 裡的基準線估算，絕不能出現「總費用低於單個險種」的數學錯誤。"""

for n in wf['nodes']:
    if n['name'] == 'Load Prompt':
        if old_block in n['parameters']['jsCode']:
            n['parameters']['jsCode'] = n['parameters']['jsCode'].replace(old_block, new_block)
            print('Updated.')
        else:
            print('ERROR: old string not found.')
        break

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print('Done.')
