import pandas as pd
from llm import ask_llm


ANALYSIS_STEPS = {
    "revenue": "Calculate total revenue.",
    "trends": "Calculate monthly sales and identify the highest and lowest sales months.",
    "products": "Calculate the top products by sales.",
    "customers": "Calculate customer statistics including total sales, number of orders, and average order value.",
    "changes": "Calculate the largest monthly sales increase and decrease."
}


def create_analysis_plan(question):
    question_lower = question.lower()

    # General business analysis: run all required analyses.
    if (
        "analyze my business" in question_lower
        or "business analysis" in question_lower
        or "analyze the business" in question_lower
    ):
        return list(ANALYSIS_STEPS.keys())

    prompt = f"""
You are an analysis planner.

User question:
{question}

Choose only the analysis steps needed to answer the question.

Available steps:
- revenue
- trends
- products
- customers
- changes

Return only the step names separated by commas.
Do not calculate anything.
"""

    try:
        response = ask_llm(prompt)
        selected = []

        for step in ANALYSIS_STEPS:
            if step in response.lower():
                selected.append(step)

        return selected
    except Exception:
        return []


def execute_analysis(file_path, selected_steps):
    df = pd.read_csv(file_path)

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        format="mixed"
    )

    results = {}

    if "revenue" in selected_steps:
        results["revenue"] = {
            "total_revenue": float(df["Sales"].sum())
        }

    if "trends" in selected_steps:
        monthly = (
            df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
            .sum()
            .sort_index()
        )

        highest_month = monthly.idxmax()
        lowest_month = monthly.idxmin()

        results["trends"] = {
            "highest_sales_month": str(highest_month),
            "highest_sales": float(monthly.max()),
            "lowest_sales_month": str(lowest_month),
            "lowest_sales": float(monthly.min())
        }

    if "products" in selected_steps:
        top_products = (
            df.groupby("Sub Category")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        results["products"] = [
            {
                "product": str(product),
                "sales": float(sales)
            }
            for product, sales in top_products.items()
        ]

    if "customers" in selected_steps:
        customer_sales = (
            df.groupby("Customer Name")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        customer_orders = (
            df.groupby("Customer Name")
            .size()
            .sort_values(ascending=False)
        )

        customer_aov = (
            df.groupby("Customer Name")["Sales"]
            .mean()
            .sort_values(ascending=False)
        )

        results["customers"] = {
            "highest_total_sales": {
                "customer": str(customer_sales.idxmax()),
                "value": float(customer_sales.max())
            },
            "highest_number_of_orders": {
                "customer": str(customer_orders.idxmax()),
                "value": int(customer_orders.max())
            },
            "highest_average_order_value": {
                "customer": str(customer_aov.idxmax()),
                "value": float(customer_aov.max())
            }
        }

    if "changes" in selected_steps:
        monthly = (
            df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
            .sum()
            .sort_index()
        )

        changes = monthly.diff().dropna()

        largest_increase_month = changes.idxmax()
        largest_decrease_month = changes.idxmin()

        results["changes"] = {
            "largest_increase": {
                "month": str(largest_increase_month),
                "change": float(changes.max())
            },
            "largest_decrease": {
                "month": str(largest_decrease_month),
                "change": float(changes.min())
            }
        }

    return results


def create_verified_facts(results):
    """
    Python creates the factual layer.
    These values are authoritative and must not be changed by Ollama.
    """

    facts = []

    if "revenue" in results:
        facts.append(
            f"Total revenue: {results['revenue']['total_revenue']}"
        )

    if "trends" in results:
        trends = results["trends"]

        facts.append(
            f"Highest sales month: {trends['highest_sales_month']} "
            f"with sales of {trends['highest_sales']}"
        )

        facts.append(
            f"Lowest sales month: {trends['lowest_sales_month']} "
            f"with sales of {trends['lowest_sales']}"
        )

    if "products" in results:
        for item in results["products"]:
            facts.append(
                f"Top product: {item['product']} "
                f"with sales of {item['sales']}"
            )

    if "customers" in results:
        customers = results["customers"]

        facts.append(
            f"Highest customer total sales: "
            f"{customers['highest_total_sales']['customer']} "
            f"with {customers['highest_total_sales']['value']}"
        )

        facts.append(
            f"Highest customer order count: "
            f"{customers['highest_number_of_orders']['customer']} "
            f"with {customers['highest_number_of_orders']['value']} orders"
        )

        facts.append(
            f"Highest customer average order value: "
            f"{customers['highest_average_order_value']['customer']} "
            f"with {customers['highest_average_order_value']['value']}"
        )

    if "changes" in results:
        changes = results["changes"]

        facts.append(
            f"Largest sales increase: "
            f"{changes['largest_increase']['month']} "
            f"with a change of {changes['largest_increase']['change']}"
        )

        facts.append(
            f"Largest sales decrease: "
            f"{changes['largest_decrease']['month']} "
            f"with a change of {changes['largest_decrease']['change']}"
        )

    return facts


def create_llm_interpretation(results):
    """
    Ollama is used only for qualitative interpretation.
    Python remains responsible for every numeric fact.
    """

    available_topics = []

    if "revenue" in results:
        available_topics.append("overall revenue performance")

    if "trends" in results:
        available_topics.append("variation in monthly sales")

    if "products" in results:
        available_topics.append("product performance concentration")

    if "customers" in results:
        available_topics.append("differences between customer metrics")

    if "changes" in results:
        available_topics.append("significant monthly changes")

    topics_text = "\n".join(f"- {topic}" for topic in available_topics)

    prompt = f"""
You are a business analyst.

Your job is ONLY to provide qualitative interpretation of the business analysis.

Available topics:
{topics_text}

STRICT RULES:
1. Do not calculate anything.
2. Do not mention any numbers, percentages, dates, amounts, or numeric values.
3. Do not invent causes.
4. Do not invent customer satisfaction, feedback, countries, markets, profit, retention, or business conditions.
5. Do not claim growth unless the provided analysis explicitly establishes it.
6. Do not state specific facts that are not directly represented by the available topics.
7. Do not repeat raw data.
8. Write exactly 2 or 3 short sentences.
9. Focus on what the analysis means at a high level.
10. Return plain text only.

Interpret the available analysis now.
"""

    try:
        response = ask_llm(prompt).strip()

        # Reliability guard:
        # If Ollama returns digits, numeric values, or an empty answer,
        # do not allow that response into the final verified answer.
        if not response or any(char.isdigit() for char in response):
            return create_safe_interpretation(results)

        return response

    except Exception:
        return create_safe_interpretation(results)


def create_safe_interpretation(results):
    """
    Deterministic fallback used if Ollama violates the interpretation rules.
    """

    sentences = []

    if "revenue" in results:
        sentences.append(
            "The analysis provides a clear view of the business's overall sales performance."
        )

    if "trends" in results:
        sentences.append(
            "Monthly sales vary over time, with identifiable stronger and weaker periods."
        )

    if "products" in results:
        sentences.append(
            "Product performance is concentrated among the strongest-selling product categories."
        )

    if "customers" in results:
        sentences.append(
            "Customer metrics show meaningful differences in sales contribution, order activity, and average order value."
        )

    if "changes" in results:
        sentences.append(
            "The monthly results contain notable increases and decreases that are useful areas for further investigation."
        )

    return " ".join(sentences[:3])


def create_recommendation_options(results):
    recommendations = {}

    if "products" in results:
        recommendations["top_products"] = (
            "Focus attention on the top-performing products identified in the sales data."
        )

    if "changes" in results:
        recommendations["investigate_changes"] = (
            "Investigate the periods with the largest sales increase and decrease "
            "to better understand changes in performance."
        )

    if "customers" in results:
        recommendations["customer_segments"] = (
            "Use the available customer sales, order, and average order value results "
            "to identify important customer segments."
        )

    if "trends" in results:
        recommendations["monthly_trends"] = (
            "Monitor monthly sales patterns and investigate unusually strong or weak periods."
        )

    return recommendations


def select_recommendations(results):
    """
    Ollama selects from predefined recommendations.
    It does not write or calculate the recommendation itself.
    """

    options = create_recommendation_options(results)

    if not options:
        return []

    options_text = "\n".join(
        f"- {key}: {value}"
        for key, value in options.items()
    )

    prompt = f"""
You are selecting business recommendations.

Available recommendations:
{options_text}

Choose at most 3 recommendations.

Return ONLY the recommendation keys separated by commas.
Do not create new recommendations.
"""

    try:
        response = ask_llm(prompt).lower()
        selected = []

        for key in options:
            if key.lower() in response:
                selected.append(key)

        return selected[:3], options

    except Exception:
        return list(options.keys())[:3], options


if __name__ == "__main__":
    file_path = "data/supermart.csv"

    question = "Analyze my business"

    selected_steps = create_analysis_plan(question)

    results = execute_analysis(
        file_path,
        selected_steps
    )

    facts = create_verified_facts(results)
    interpretation = create_llm_interpretation(results)
    recommendation_keys = select_recommendations(results)
    recommendation_options = create_recommendation_options(results)

    print("\nBusiness Performance Analysis\n")

    for fact in facts:
        print(fact)

    print("\nAI Interpretation:")
    print(interpretation)

    print("\nRecommendations:")
    for key in recommendation_keys:
        print(f"- {recommendation_options[key]}")