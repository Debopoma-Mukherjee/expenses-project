from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Global DataFrame to store expenses
expenses_df = pd.DataFrame(columns=["amount", "category"])

def home(request):
    global expenses_df

    # Initialize salary in session if not set
    if "salary" not in request.session:
        request.session["salary"] = 0

    if request.method == "POST":
        # Add expense
        if "add_expense" in request.POST:
            amount = request.POST.get("amount")
            category = request.POST.get("category")
            if amount and category:
                try:
                    amount = float(amount)
                except ValueError:
                    amount = 0
                if amount > 0:
                    expenses_df.loc[len(expenses_df)] = [amount, category]

        # Set salary
        elif "set_salary" in request.POST:
            salary = request.POST.get("salary")
            try:
                request.session["salary"] = float(salary)
            except (ValueError, TypeError):
                request.session["salary"] = 0

        # Reset all expenses
        elif "reset" in request.POST:
            expenses_df = pd.DataFrame(columns=["amount", "category"])

        return redirect("home")

    # Calculate total expense
    total_expense = expenses_df["amount"].sum()
    salary = request.session.get("salary", 0)
    alert = ""
    if salary > 0 and total_expense > 0.8 * salary:
        alert = "⚠️ Warning: Expenses exceeded 80% of your salary!"

    return render(request, "home.html", {
        "expenses": expenses_df.to_dict(orient="records"),
        "total_expense": total_expense,
        "salary": salary,
        "alert": alert
    })


# Charts remain the same as before
def bar_chart(request):
    global expenses_df
    if expenses_df.empty:
        return HttpResponse("No data to display")

    grouped = expenses_df.groupby("category")["amount"].sum()
    fig, ax = plt.subplots()
    ax.bar(grouped.index, grouped.values, color="skyblue")
    ax.set_title("Expenses by Category")
    ax.set_ylabel("Amount")
    ax.set_xlabel("Category")
    response = HttpResponse(content_type="image/png")
    fig.savefig(response, format="png")
    plt.close(fig)
    return response

def pie_chart(request):
    global expenses_df
    if expenses_df.empty:
        return HttpResponse("No data to display")

    grouped = expenses_df.groupby("category")["amount"].sum()
    fig, ax = plt.subplots()
    ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")
    ax.set_title("Expense Distribution")
    response = HttpResponse(content_type="image/png")
    fig.savefig(response, format="png")
    plt.close(fig)
    return response
