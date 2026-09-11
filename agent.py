from llm import ask_llm
from tools import TOOLS
from business_analysis import (
    create_analysis_plan,
    execute_analysis,
    create_llm_interpretation,
    select_recommendations
)


file_path = "data/supermart.csv"


tools_description = """
Available tools:

1. get_total_revenue
   Description: Calculate the total revenue from the sales data.

2. get_monthly_sales
   Description: Calculate total sales for each month.

3. get_top_products
   Description: Find the top products based on total sales.

4. get_customer_statistics
   Description: Analyze customer sales, orders, and average order value.

5. compare_periods
   Description: Compare sales between two periods such as Q1 and Q2.
"""


def create_chart_data(results):

    chart_data = {
        "type": None,
        "data": []
    }

    if "get_top_products" in results:

        products = results["get_top_products"]

        if isinstance(products, dict) and "error" in products:
            return chart_data

        chart_data["type"] = "top_products"

        for _, row in products.iterrows():

            chart_data["data"].append({
                "label": str(row["Sub Category"]),
                "value": int(row["Sales"])
            })

        return chart_data

    if "get_monthly_sales" in results:

        monthly_data = TOOLS["get_monthly_sales"](
            file_path
        )

        chart_data["type"] = "monthly_sales"

        for _, row in monthly_data.iterrows():

            chart_data["data"].append({
                "label": str(row["Order Date"]),
                "value": int(row["Sales"])
            })

        return chart_data

    if "compare_periods" in results:

        comparison = results["compare_periods"]

        if isinstance(comparison, dict) and "error" in comparison:
            return chart_data

        if not isinstance(comparison, dict):
            return chart_data

        if (
            "period1" not in comparison
            or "period2" not in comparison
            or "period1_sales" not in comparison
            or "period2_sales" not in comparison
        ):
            return chart_data

        chart_data["type"] = "compare_periods"

        chart_data["data"] = [
            {
                "label": comparison["period1"],
                "value": int(
                    comparison["period1_sales"]
                )
            },
            {
                "label": comparison["period2"],
                "value": int(
                    comparison["period2_sales"]
                )
            }
        ]

        return chart_data

    return chart_data


def run_business_analysis(question):

    selected_steps = create_analysis_plan(question)

    results = execute_analysis(
        file_path,
        selected_steps
    )

    interpretation = create_llm_interpretation(
        results
    )

    selected_recommendations, recommendation_options = (
        select_recommendations(results)
    )

    final_answer_parts = []

    final_answer_parts.append(
        "Business Performance Analysis"
    )

    if "revenue" in results:

        final_answer_parts.append(
            f"Total revenue: "
            f"{int(results['revenue']['total_revenue']):,}."
        )

    if "trends" in results:

        trends = results["trends"]

        final_answer_parts.append(
            f"Highest sales month: "
            f"{trends['highest_sales_month']} "
            f"with sales of "
            f"{trends['highest_sales']:,}."
        )

        final_answer_parts.append(
            f"Lowest sales month: "
            f"{trends['lowest_sales_month']} "
            f"with sales of "
            f"{trends['lowest_sales']:,}."
        )

    if interpretation:

        final_answer_parts.append(
            f"AI Interpretation:\n{interpretation}"
        )

    if "products" in results:

        products = results["products"]

        products_text = "Top Products:"

        for item in products:

            products_text += (
                f"\n- {item['product']}: "
                f"{int(item['sales']):,}"
            )

        final_answer_parts.append(
            products_text
        )

    if "customers" in results:

        customers = results["customers"]

        final_answer_parts.append(
            "Customer Highlights:\n"
            f"- Highest total sales: "
            f"{customers['highest_total_sales']['customer']} "
            f"({customers['highest_total_sales']['value']:,})\n"
            f"- Highest number of orders: "
            f"{customers['highest_number_of_orders']['customer']} "
            f"({customers['highest_number_of_orders']['value']:,})\n"
            f"- Highest average order value: "
            f"{customers['highest_average_order_value']['customer']} "
            f"({customers['highest_average_order_value']['value']:.2f})"
        )

    if "changes" in results:

        changes = results["changes"]

        final_answer_parts.append(
            "Significant Changes:\n"
            f"- Largest sales increase: "
            f"{changes['largest_increase']['month']} "
            f"({changes['largest_increase']['change']:+,.0f})\n"
            f"- Largest sales decrease: "
            f"{changes['largest_decrease']['month']} "
            f"({changes['largest_decrease']['change']:+,.0f})"
        )

    if selected_recommendations:

        recommendations_text = "Recommendations:"

        for recommendation_key in selected_recommendations:

            recommendations_text += (
                f"\n- "
                f"{recommendation_options[recommendation_key]}"
            )

        final_answer_parts.append(
            recommendations_text
        )

    return "\n\n".join(final_answer_parts)


def run_agent(question):

    question_lower = question.lower()

    if (
        "analyze my business" in question_lower
        or "business analysis" in question_lower
        or "analyze the business" in question_lower
    ):

        return run_business_analysis(question)

    selection_prompt = f"""
You are the tool selection system for Smart Business Analyst.

{tools_description}

User question:
{question}

Choose ONLY the tools that are necessary to answer the question.

Rules:
- Use the minimum number of tools required.
- Select every tool that is necessary.
- Do not select unrelated tools.
- Return only exact tool names.
- Return one tool name per line.
- Do not explain anything.

Answer:
"""

    try:

        raw_response = ask_llm(
            selection_prompt
        ).strip()

    except Exception:

        raw_response = ""

    selected_tools = []

    if (
        "compare" in question_lower
        or "compared" in question_lower
    ):

        selected_tools.append(
            "compare_periods"
        )

    if "revenue" in question_lower:

        selected_tools.append(
            "get_total_revenue"
        )

    if (
        "monthly" in question_lower
        or "month" in question_lower
    ):

        selected_tools.append(
            "get_monthly_sales"
        )

    if (
        "top product" in question_lower
        or "top products" in question_lower
    ):

        selected_tools.append(
            "get_top_products"
        )

    if (
        "customer" in question_lower
        or "customers" in question_lower
        or "top customer" in question_lower
        or "top customers" in question_lower
        or "highest number of orders" in question_lower
        or "highest average order value" in question_lower
        or "average order value" in question_lower
    ):

        selected_tools.append(
            "get_customer_statistics"
        )

    selected_tools = list(
        dict.fromkeys(selected_tools)
    )

    if not selected_tools:

        for line in raw_response.splitlines():

            line = line.strip()

            if (
                line in TOOLS
                and line not in selected_tools
            ):

                selected_tools.append(
                    line
                )

    period1 = None
    period2 = None

    if "compare_periods" in selected_tools:

        parameter_prompt = f"""
You are a parameter extraction system for Smart Business Analyst.

User question:
{question}

Extract the two comparison periods.

Return ONLY:

period1=YYYY-QX
period2=YYYY-QX

Example:

Compare Q1 2017 with Q3 2018

period1=2017-Q1
period2=2018-Q3
"""

        try:

            parameter_response = ask_llm(
                parameter_prompt
            ).strip()

        except Exception:

            parameter_response = ""

        for line in parameter_response.splitlines():

            line = line.strip()

            if line.startswith("period1="):

                period1 = line.replace(
                    "period1=",
                    ""
                ).strip()

            elif line.startswith("period2="):

                period2 = line.replace(
                    "period2=",
                    ""
                ).strip()

    if not selected_tools:

        return (
            "I could not understand the business question. "
            "Please ask about revenue, monthly sales, "
            "top products, customers, or period comparisons.",
            {
                "type": None,
                "data": []
            }
        )

    results = {}

    for selected_tool in selected_tools:

        try:

            if selected_tool == "compare_periods":

                if period1 and period2:

                    result = TOOLS[selected_tool](
                        file_path,
                        period1,
                        period2
                    )

                else:

                    result = {
                        "error":
                            "Could not extract comparison periods."
                    }

            elif selected_tool == "get_monthly_sales":

                monthly_data = TOOLS[selected_tool](
                    file_path
                )

                highest_month = monthly_data.loc[
                    monthly_data["Sales"].idxmax()
                ]

                lowest_month = monthly_data.loc[
                    monthly_data["Sales"].idxmin()
                ]

                yearly_sales = (
                    monthly_data.assign(
                        Year=monthly_data[
                            "Order Date"
                        ].str[:4]
                    )
                    .groupby("Year")["Sales"]
                    .sum()
                    .to_dict()
                )

                result = {

                    "highest_sales_month":
                        highest_month["Order Date"],

                    "highest_sales":
                        int(
                            highest_month["Sales"]
                        ),

                    "lowest_sales_month":
                        lowest_month["Order Date"],

                    "lowest_sales":
                        int(
                            lowest_month["Sales"]
                        ),

                    "yearly_sales": {

                        year: int(sales)

                        for year, sales
                        in yearly_sales.items()

                    }
                }

            elif selected_tool == "get_customer_statistics":

                customer_data = TOOLS[selected_tool](
                    file_path
                )

                highest_sales = customer_data.loc[
                    customer_data[
                        "Total_Sales"
                    ].idxmax()
                ]

                highest_orders = customer_data.loc[
                    customer_data[
                        "Number_of_Orders"
                    ].idxmax()
                ]

                highest_aov = customer_data.loc[
                    customer_data[
                        "Average_Order_Value"
                    ].idxmax()
                ]

                result = {

                    "highest_total_sales_customer":
                        highest_sales[
                            "Customer Name"
                        ],

                    "highest_total_sales":
                        int(
                            highest_sales[
                                "Total_Sales"
                            ]
                        ),

                    "highest_orders_customer":
                        highest_orders[
                            "Customer Name"
                        ],

                    "highest_number_of_orders":
                        int(
                            highest_orders[
                                "Number_of_Orders"
                            ]
                        ),

                    "highest_aov_customer":
                        highest_aov[
                            "Customer Name"
                        ],

                    "highest_average_order_value":
                        float(
                            highest_aov[
                                "Average_Order_Value"
                            ]
                        )
                }

            else:

                result = TOOLS[selected_tool](
                    file_path
                )

            results[selected_tool] = result

        except Exception as error:

            results[selected_tool] = {
                "error": str(error)
            }

    final_answer_parts = []

    if "get_total_revenue" in results:

        result = results["get_total_revenue"]

        if (
            isinstance(result, dict)
            and "error" in result
        ):

            final_answer_parts.append(
                "I could not calculate the total revenue "
                "because an error occurred."
            )

        else:

            total_revenue = int(result)

            final_answer_parts.append(
                f"The total revenue is "
                f"{total_revenue:,}."
            )

    if "get_top_products" in results:

        products = results[
            "get_top_products"
        ]

        if (
            isinstance(products, dict)
            and "error" in products
        ):

            final_answer_parts.append(
                "I could not retrieve the top products "
                "because an error occurred."
            )

        else:

            text = (
                "The top products based on sales are:\n"
            )

            for _, row in products.iterrows():

                product_name = row[
                    "Sub Category"
                ]

                sales = int(
                    row["Sales"]
                )

                text += (
                    f"- {product_name}: "
                    f"{sales:,}\n"
                )

            final_answer_parts.append(
                text.strip()
            )

    if "get_customer_statistics" in results:

        customer_data = results[
            "get_customer_statistics"
        ]

        if (
            isinstance(customer_data, dict)
            and "error" in customer_data
        ):

            final_answer_parts.append(
                "I could not retrieve the customer "
                "statistics because an error occurred."
            )

        elif (
            "highest total sales"
            in question_lower
            and "orders"
            not in question_lower
            and "average"
            not in question_lower
        ):

            customer_name = (
                customer_data[
                    "highest_total_sales_customer"
                ]
            )

            total_sales = int(
                customer_data[
                    "highest_total_sales"
                ]
            )

            final_answer_parts.append(
                f"{customer_name} is the customer "
                f"with the highest total sales: "
                f"{total_sales:,}."
            )

        elif (
            "highest number of orders"
            in question_lower
        ):

            customer_name = (
                customer_data[
                    "highest_orders_customer"
                ]
            )

            number_of_orders = int(
                customer_data[
                    "highest_number_of_orders"
                ]
            )

            final_answer_parts.append(
                f"{customer_name} has the highest "
                f"number of orders: "
                f"{number_of_orders:,}."
            )

        elif (
            "average order value"
            in question_lower
            or "highest average"
            in question_lower
        ):

            customer_name = (
                customer_data[
                    "highest_aov_customer"
                ]
            )

            average_order_value = (
                customer_data[
                    "highest_average_order_value"
                ]
            )

            final_answer_parts.append(
                f"{customer_name} has the highest "
                f"average order value: "
                f"{average_order_value:.2f}."
            )

        else:

            final_answer_parts.append(
                "Top Customer Highlights:\n"
                f"- Highest total sales: "
                f"{customer_data['highest_total_sales_customer']} "
                f"({int(customer_data['highest_total_sales']):,})\n"
                f"- Highest number of orders: "
                f"{customer_data['highest_orders_customer']} "
                f"({int(customer_data['highest_number_of_orders']):,})\n"
                f"- Highest average order value: "
                f"{customer_data['highest_aov_customer']} "
                f"({float(customer_data['highest_average_order_value']):.2f})"
            )

    if "compare_periods" in results:

        comparison = results[
            "compare_periods"
        ]

        if (
            isinstance(comparison, dict)
            and "error" in comparison
        ):

            final_answer_parts.append(
                "I could not compare the requested periods. "
                "Please make sure you provide two valid periods "
                "such as Q1 2018 and Q2 2018."
            )

        elif isinstance(comparison, dict):

            period1 = comparison["period1"]
            period2 = comparison["period2"]

            sales1 = int(
                comparison["period1_sales"]
            )

            sales2 = int(
                comparison["period2_sales"]
            )

            difference = int(
                comparison["difference"]
            )

            percentage_change = float(
                comparison["percentage_change"]
            )

            if difference >= 0:

                comparison_text = (
                    f"Sales increased from "
                    f"{sales1:,} in {period1} "
                    f"to {sales2:,} in {period2}. "
                    f"This represents an increase "
                    f"of {difference:,} "
                    f"({percentage_change:.2f}%)."
                )

            else:

                comparison_text = (
                    f"Sales decreased from "
                    f"{sales1:,} in {period1} "
                    f"to {sales2:,} in {period2}. "
                    f"This represents a decrease "
                    f"of {abs(difference):,} "
                    f"({abs(percentage_change):.2f}%)."
                )

            final_answer_parts.append(
                comparison_text
            )

    if "get_monthly_sales" in results:

        monthly_result = results[
            "get_monthly_sales"
        ]

        if (
            isinstance(monthly_result, dict)
            and "error" in monthly_result
        ):

            final_answer_parts.append(
                "I could not retrieve the monthly sales "
                "because an error occurred."
            )

        else:

            monthly_text = (
                f"The highest sales month was "
                f"{monthly_result['highest_sales_month']} "
                f"with sales of "
                f"{int(monthly_result['highest_sales']):,}. "
                f"The lowest sales month was "
                f"{monthly_result['lowest_sales_month']} "
                f"with sales of "
                f"{int(monthly_result['lowest_sales']):,}."
            )

            final_answer_parts.append(
                monthly_text
            )

    if not final_answer_parts:

        final_answer_parts.append(
            "I could not generate an answer for this question. "
            "Please try asking about revenue, monthly sales, "
            "top products, customers, or period comparisons."
        )

    final_answer = "\n\n".join(
        final_answer_parts
    )

    chart_data = create_chart_data(
        results
    )

    return final_answer, chart_data


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    )

    answer, chart_data = run_agent(
        question
    )

    print()
    print("Final Answer:")
    print(answer)

    print()
    print("Chart Data:")
    print(chart_data)