import html
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_statistics_chart(statistics, processed_dir="processed"):
    os.makedirs(processed_dir, exist_ok=True)
    path = os.path.join(processed_dir, "statistics.png")
    data = _nonzero_statistics(statistics)

    labels = list(data.keys()) or ["no_files"]
    counts = list(data.values()) or [0]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, counts, color="#3b82f6")
    plt.title("Processed mail by category")
    plt.xlabel("Category")
    plt.ylabel("Messages")
    plt.xticks(rotation=45, ha="right")
    plt.bar_label(bars, padding=3)
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()

    return path


def save_html_report(statistics, processed_dir="processed", chart_filename="statistics.png"):
    os.makedirs(processed_dir, exist_ok=True)
    path = os.path.join(processed_dir, "report.html")

    total = sum(statistics.values())
    unknown_count = _count_by_marker(statistics, "unknown")
    quarantine_count = _count_by_marker(statistics, "quarantine")
    top_categories = sorted(
        _nonzero_statistics(statistics).items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    with open(path, "w", encoding="utf-8") as file:
        file.write(
            _build_html_report(
                statistics=statistics,
                total=total,
                unknown_count=unknown_count,
                quarantine_count=quarantine_count,
                top_categories=top_categories,
                chart_filename=chart_filename,
            )
        )

    return path


def save_processing_report(statistics, processed_dir="processed"):
    chart_path = save_statistics_chart(statistics, processed_dir)
    report_path = save_html_report(
        statistics,
        processed_dir,
        chart_filename=os.path.basename(chart_path),
    )
    return chart_path, report_path


def _nonzero_statistics(statistics):
    return {
        category: count
        for category, count in sorted(statistics.items())
        if count > 0
    }


def _count_by_marker(statistics, marker):
    return sum(count for category, count in statistics.items() if marker in category)


def _build_html_report(
    *,
    statistics,
    total,
    unknown_count,
    quarantine_count,
    top_categories,
    chart_filename,
):
    table_rows = "\n".join(
        f"<tr><td>{html.escape(category)}</td><td>{count}</td></tr>"
        for category, count in sorted(statistics.items())
    )
    top_items = "\n".join(
        f"<li>{html.escape(category)}: {count}</li>"
        for category, count in top_categories
    ) or "<li>No processed files</li>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Mail Processing Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 32px;
      color: #1f2937;
    }}
    h1, h2 {{
      color: #111827;
    }}
    .summary {{
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      margin: 16px 0 24px;
    }}
    .metric {{
      border: 1px solid #d1d5db;
      border-radius: 6px;
      padding: 12px 16px;
      min-width: 160px;
      background: #f9fafb;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      margin-top: 4px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 12px;
    }}
    th, td {{
      border: 1px solid #d1d5db;
      padding: 8px 10px;
      text-align: left;
    }}
    th {{
      background: #f3f4f6;
    }}
    img {{
      max-width: 100%;
      border: 1px solid #d1d5db;
      border-radius: 6px;
    }}
  </style>
</head>
<body>
  <h1>Mail Processing Report</h1>

  <section class="summary">
    <div class="metric">Total processed<strong>{total}</strong></div>
    <div class="metric">Unknown<strong>{unknown_count}</strong></div>
    <div class="metric">Quarantine<strong>{quarantine_count}</strong></div>
  </section>

  <h2>Category chart</h2>
  <img src="{html.escape(chart_filename)}" alt="Processed mail by category">

  <h2>Top categories</h2>
  <ol>
    {top_items}
  </ol>

  <h2>Full statistics</h2>
  <table>
    <thead>
      <tr><th>Category</th><th>Messages</th></tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</body>
</html>
"""
