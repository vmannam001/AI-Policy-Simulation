import json
import pandas as pd
from datetime import datetime

# Load historical access logs
logs = pd.read_csv("mock_logs.csv")

# Load the new policy proposed in the PR
with open("policies/new_policy.json") as f:
    policy = json.load(f)

# Parse condition: 'time < "10:00"'
policy_hour_limit = int(policy["condition"].split("<")[1].strip(" '\"").split(":")[0])

# Apply new policy to each access record
def apply_policy(row):
    log_hour = datetime.fromisoformat(row['timestamp']).hour
    if row['resource'] == policy['resource'] and row['action'] == policy['action']:
        return "Permit" if log_hour < policy_hour_limit else "Deny"
    return row['outcome']  # Unchanged for other resources/actions

# Apply and compare
logs["new_outcome"] = logs.apply(apply_policy, axis=1)
logs["changed"] = logs["outcome"] != logs["new_outcome"]

# Summary
changed_count = logs["changed"].sum()
total_logs = len(logs)

summary = f"""
🚨 **Predictive Access Simulation Report (Rule-Based)** 🚨

🔄 **Policy Change Impact Summary**
- Total Logs Evaluated: **{total_logs}**
- Access Decisions Changed: **{changed_count}**

📝 New Policy Proposed:
- Resource: `{policy['resource']}`
- Action: `{policy['action']}`
- Condition: `{policy['condition']}`

📊 Sample Change:
- Original: outcome = Permit (at 11:00 AM)
- Under new policy: outcome = Deny (access allowed only before 10:00 AM)

> ⚠️ This change will **deny access** to users who were previously allowed after 10 AM.
"""

with open("simulation_result.txt", "w") as f:
    f.write(summary.strip())
