import json
from typing import List, Dict

def render_header(title: str) -> str:
    return f"""
    <header style="padding:1em;background:#1a1a1a;color:white;text-align:center">
        <h1>{title}</h1>
    </header>
    """

def render_recent_tasks(recent_tasks: List[Dict]) -> str:
    items = ""
    for task in recent_tasks:
        items += f"""
        <tr>
            <td>{task.get("task_id")}</td>
            <td>{task.get("model_id")}</td>
            <td>{task.get("timestamp")}</td>
            <td>{task.get("latency", 'N/A')}</td>
        </tr>
        """
    return f"""
    <section style="padding:1em">
        <h2>Recent Inference Tasks</h2>
        <table border="1" style="width:100%;text-align:left">
            <tr>
                <th>Task ID</th>
                <th>Model</th>
                <th>Timestamp</th>
                <th>Latency</th>
            </tr>
            {items}
        </table>
    </section>
    """

def render_node_status(nodes: Dict[str, Dict]) -> str:
    rows = ""
    for node_id, status in nodes.items():
        rows += f"""
        <tr>
            <td>{node_id}</td>
            <td>{status.get('status', 'offline')}</td>
            <td>{status.get('latency', 'unknown')}</td>
            <td>{status.get('last_seen')}</td>
        </tr>
        """
    return f"""
    <section style="padding:1em">
        <h2>AI Node Health</h2>
        <table border="1" style="width:100%">
            <tr>
                <th>Node ID</th>
                <th>Status</th>
                <th>Latency (ms)</th>
                <th>Last Seen</th>
            </tr>
            {rows}
        </table>
    </section>
    """

def render_model_usage(model_stats: Dict[str, int]) -> str:
    rows = ""
    for model, count in model_stats.items():
        rows += f"<li>{model}: {count} inferences</li>"
    return f"""
    <section style="padding:1em">
        <h2>Model Usage</h2>
        <ul>
            {rows}
        </ul>
    </section>
    """

def render_sentiment_chart(sentiment_data: List[Dict[str, str]]) -> str:
    labels = [d['label'] for d in sentiment_data]
    values = [d['value'] for d in sentiment_data]

    return f"""
    <section style="padding:1em">
        <h2>Sentiment Trends</h2>
        <canvas id="sentimentChart"></canvas>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('sentimentChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        label: 'Sentiment',
                        data: {json.dumps(values)},
                        backgroundColor: 'rgba(75, 192, 192, 0.7)'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>
    </section>
    """

def render_full_dashboard(recent_tasks, node_status, model_usage, sentiment) -> str:
    html = f"""
    <html>
    <head>
        <title>PARALLAX Dashboard</title>
    </head>
    <body style="font-family:sans-serif;background:#f5f5f5">
        {render_header("PARALLAX Dashboard")}
        {render_recent_tasks(recent_tasks)}
        {render_node_status(node_status)}
        {render_model_usage(model_usage)}
        {render_sentiment_chart(sentiment)}
    </body>
    </html>
    """
    return html
