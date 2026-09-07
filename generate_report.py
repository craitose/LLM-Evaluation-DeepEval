import json
import os
import re

# Configuration paths
json_path = ".deepeval/.latest_test_run.json"
html_output_path = "deepeval_report.html"

if not os.path.exists(json_path):
    print(f"Error: Target file not found at local path: {json_path}")
    exit(1)

with open(json_path, "r", encoding="utf-8", errors="ignore") as f:
    raw_data = f.read().strip()
    # Structural repair guard if file was abruptly cut off mid-stream
    if not raw_data.endswith("}"):
        print(
            "Heuristic Guard: Truncated JSON detected. Re-balancing structures safely..."
        )
        if "metricsData" in raw_data and not raw_data.endswith("]"):
            raw_data += "}]}]}}"
        else:
            raw_data += "]}"

try:
    data = json.loads(raw_data)
except json.JSONDecodeError as err:
    print(f"Aborting execution. Structural recovery fell short: {err}")
    exit(1)

test_run_data = data.get("testRunData", {})
test_file = test_run_data.get("testFile", "test_complete.py")
test_cases = test_run_data.get("testCases", [])

# Dashboard analytics processing
total_cases = len(test_cases)
passed_cases = sum(1 for case in test_cases if case.get("success", False))
failed_cases = total_cases - passed_cases
success_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0.0

# Scaffold dashboard output with modern CSS layers and interactive controls
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DeepEval Exec Summary Dashboard</title>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; margin: 30px; background-color: #f8fafc; color: #0f172a; }}
        .header {{ background: #0f172a; color: white; padding: 24px; border-radius: 12px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0; font-size: 26px; font-weight: 700; }}
        .header p {{ margin: 8px 0 0 0; color: #94a3b8; font-size: 15px; }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e2e8f0; }}
        .stat-card .val {{ font-size: 28px; font-weight: 800; margin-top: 5px; }}
        .stat-card.pass .val {{ color: #10b981; }}
        .stat-card.fail .val {{ color: #ef4444; }}
        
        .filter-container {{ margin-bottom: 20px; display: flex; gap: 10px; align-items: center; }}
        .btn {{ padding: 8px 16px; border-radius: 6px; border: 1px solid #cbd5e1; background: white; cursor: pointer; font-size: 14px; font-weight: 500; transition: 0.2s; }}
        .btn:hover {{ background: #f1f5f9; }}
        .btn.active {{ background: #0f172a; color: white; border-color: #0f172a; }}

        .card {{ background: white; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 25px; overflow: hidden; }}
        .card-header {{ padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; background: #fafafa; }}
        .card-title {{ font-size: 15px; font-weight: 600; color: #334155; word-break: break-all; margin-right: 15px; }}
        .card-body {{ padding: 20px; }}
        
        .badge {{ padding: 4px 10px; font-size: 12px; font-weight: 700; border-radius: 6px; text-transform: uppercase; }}
        .badge.passed {{ background-color: #d1fae5; color: #065f46; }}
        .badge.failed {{ background-color: #fee2e2; color: #991b1b; }}
        
        .io-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
        .io-box {{ background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; }}
        .io-box h4 {{ margin: 0 0 8px 0; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .io-box pre {{ margin: 0; white-space: pre-wrap; font-family: monospace; font-size: 13px; color: #334155; line-height: 1.5; }}
        
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
        th {{ background: #f1f5f9; padding: 12px; color: #475569; font-weight: 600; border-bottom: 2px solid #cbd5e1; }}
        td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
        .err-msg {{ color: #dc2626; font-size: 13px; background: #fef2f2; padding: 8px; border-radius: 6px; border: 1px solid #fca5a5; display: inline-block; }}
    </style>
    <script>
        function filterCards(status, event) {{
            document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('.card').forEach(card => {{
                if (status === 'all') {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = card.classList.contains(status) ? 'block' : 'none';
                }}
            }});
        }}
    </script>
</head>
<body>

<div class="header">
    <h1>DeepEval Exec Summary Dashboard</h1>
    <p>Target Suite File: <strong>{test_file}</strong></p>
</div>

<div class="metrics-grid">
    <div class="stat-card">
        <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Total Assertions</div>
        <div class="val" style="color: #0f172a;">{total_cases}</div>
    </div>
    <div class="stat-card pass">
        <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Passed Test Cases</div>
        <div class="val">{passed_cases}</div>
    </div>
    <div class="stat-card fail">
        <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Failed Test Cases</div>
        <div class="val">{failed_cases}</div>
    </div>
    <div class="stat-card">
        <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Success Rate</div>
        <div class="val" style="color: #2563eb;">{success_rate:.1f}%</div>
    </div>
</div>

<div class="filter-container">
    <button class="btn active" onclick="filterCards('all', event)">Show All ({total_cases})</button>
    <button class="btn" onclick="filterCards('passed', event)">Passed Only ({passed_cases})</button>
    <button class="btn" onclick="filterCards('failed', event)">Failed Only ({failed_cases})</button>
</div>
"""

for idx, case in enumerate(test_cases):
    is_ok = case.get("success", False)
    cls_status = "passed" if is_ok else "failed"

    # Extract raw case title name
    raw_name = case.get("name", "Unnamed Case")

    # 1. Clean the messy trailing context tag suffix at the bracket edge
    clean_name = re.sub(r"-retrieved_knowledge_context\d+\]$", "]", raw_name)

    # 2. Swap literal string '\n' markers with normal whitespace dividers
    clean_name = clean_name.replace(r"\n\n", " ").replace(r"\n", " ")

    # 3. Add a clean space separator right before the bracket starts
    clean_name = clean_name.replace("[", " [")

    html_content += f"""
    <div class="card {cls_status}">
        <div class="card-header">
            <div class="card-title"><strong>Case #{idx + 1}:</strong> {clean_name} </div>
            <span class="badge {cls_status}">{cls_status}</span>
        </div>
        <div class="card-body">
            <div class="io-grid">
                <div class="io-box">
                    <h4>Input Prompt</h4>
                    <pre>{case.get("input", "N/A")}</pre>
                </div>
                <div class="io-box">
                    <h4>Actual Response Output</h4>
                    <pre>{case.get("actualOutput", "N/A")}</pre>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">Metric Name</th>
                        <th style="width: 12%;">Score</th>
                        <th style="width: 12%;">Threshold</th>
                        <th style="width: 56%;">Evaluation Remarks</th>
                    </tr>
                </thead>
                <tbody>
    """

    for m in case.get("metricsData", []):
        m_ok = m.get("success", False)
        m_style = (
            "color: #059669; font-weight: 600;"
            if m_ok
            else "color: #dc2626; font-weight: 600;"
        )
        m_err = m.get("error")

        if m_err:
            score_txt = "-"
            lbl_cls = "failed"
            remark = (
                f'<div class="err-msg"><strong>Timeout/Crash:</strong> {m_err}</div>'
            )
        else:
            s_val = m.get("score")
            score_txt = (
                f"{s_val:.2f}" if isinstance(s_val, (int, float)) else str(s_val)
            )
            lbl_cls = "passed" if m_ok else "failed"
            remark = m.get("reason", "No evaluation summary reason provided.")

        html_content += f"""
                    <tr>
                        <td style="{m_style}">{m.get("name")}</td>
                        <td><span class="badge {lbl_cls}">{score_txt}</span></td>
                        <td>{m.get("threshold", "N/A")}</td>
                        <td>{remark}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    """

html_content += """</body></html>"""

with open(html_output_path, "w", encoding="utf-8") as out:
    out.write(html_content)

print(f"Successfully exported interactive matrix report sheet to: '{html_output_path}'")
