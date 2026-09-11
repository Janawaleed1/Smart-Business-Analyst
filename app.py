import gradio as gr
import matplotlib.pyplot as plt

from agent import run_agent


def create_plot(chart_data):

    if not chart_data or not chart_data.get("data"):
        return None

    chart_type = chart_data["type"]
    data = chart_data["data"]

    labels = [item["label"] for item in data]
    values = [item["value"] for item in data]

    fig, ax = plt.subplots(figsize=(10, 5))

    if chart_type == "top_products":

        ax.bar(labels, values)

        ax.set_title("Top Products by Sales")
        ax.set_xlabel("Product")
        ax.set_ylabel("Sales")

        plt.xticks(rotation=45, ha="right")

    elif chart_type == "monthly_sales":

        ax.plot(labels, values, marker="o")

        ax.set_title("Monthly Sales")
        ax.set_xlabel("Month")
        ax.set_ylabel("Sales")

        plt.xticks(rotation=45, ha="right")

    elif chart_type == "compare_periods":

        ax.bar(labels, values)

        ax.set_title("Sales Comparison")
        ax.set_xlabel("Period")
        ax.set_ylabel("Sales")

    plt.tight_layout()

    return fig


def chat_with_agent(message, history):

    answer, chart_data = run_agent(message)

    plot = create_plot(chart_data)

    return answer, plot


with gr.Blocks() as demo:

    plot = gr.Plot(
        label="Business Visualization"
    )

    gr.ChatInterface(

        fn=chat_with_agent,

        title="Smart Business Analyst",

        description="Ask questions about your business sales data.",

        textbox=gr.Textbox(
            placeholder="Ask a business question...",
            container=True
        ),

        additional_outputs=[plot]
    )


demo.launch()