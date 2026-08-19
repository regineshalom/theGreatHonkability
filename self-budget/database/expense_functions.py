## Expense Functions

from sqlalchemy import text
from database.db_engine import engine

def insert_expense(expense_name: str, expense_amount: float, date_of_message: str, category_name: str, subcategory: str = None, telegram_chat_id: int = None, telegram_message_id: int = None) -> None:
    """
    Insert an expense into the database.

    Args:
        expense_name (str): The name of the expense.
        expense_amount (float): The amount of the expense.
        date_of_message (str): The date and time of the message.
        category_name (str): The name of the category.
        subcategory (str, optional): The name of the subcategory. Defaults to None.
        telegram_chat_id (int): The ID of the Telegram chat. Defaults to None.
        telegram_message_id (int): The ID of the Telegram message. Defaults to None.
    """
    with engine.begin() as connection:

        if subcategory is None:
            query = text("""
                select cat_id from category where cat_name = :category_name and sub_cat is null
            """)
            result = connection.execute(query, {"category_name": category_name})
        else:
            query = text("""
                select cat_id from category where cat_name = :category_name and sub_cat = :subcategory
            """)
            result = connection.execute(query, {"category_name": category_name, "subcategory": subcategory})

        cat_id_row = result.fetchone()

        if cat_id_row is None:
            raise ValueError(f"Category '{category_name}' with subcategory '{subcategory}' not found in the database.")

        cat_id = cat_id_row[0]
        print(cat_id)

        query = text("""
            insert into expenses (exp_name, exp_amount, exp_datetime, cat_id, telegram_chat_id, telegram_message_id)
            values (:expense_name, :expense_amount, :date_of_message, :cat_id, :telegram_chat_id, :telegram_message_id)
        """)
        connection.execute(query, {
            "expense_name": expense_name,
            "expense_amount": expense_amount,
            "date_of_message": date_of_message,
            "cat_id": cat_id,
            "telegram_chat_id": telegram_chat_id,
            "telegram_message_id": telegram_message_id,
            "subcategory": subcategory
        })

        ## to return the remaining budget for all categories
        query = text("""
            select c.cat_name, c.sub_cat, c.cat_budget - ifnull(sum(e.exp_amount), 0) as remaining_budget
            from category c
            left join expenses e on c.cat_id = e.cat_id
            group by c.cat_id
        """)
        result = connection.execute(query)
        remaining_budgets = result.fetchall()

        return remaining_budgets

    

def update_expense(expense_name: str, expense_amount: float, date_of_message: str, category_name: str, subcategory: str = None, telegram_chat_id: int = None, telegram_message_id: int = None) -> None:
    """
    Update an existing expense in the database.

    Args:
        expense_name (str): The new name of the expense.
        expense_amount (float): The new amount of the expense.
        date_of_message (str): The new date and time of the message.
        category_name (str): The new name of the category.
        subcategory (str, optional): The new name of the subcategory. Defaults to None.
        telegram_chat_id (int): The ID of the Telegram chat. Defaults to None.
        telegram_message_id (int): The ID of the Telegram message. Defaults to None
    """
    with engine.begin() as connection:

        if subcategory is None:
            query = text("""
                select cat_id from category where cat_name = :category_name and sub_cat is null
            """)
            result = connection.execute(query, {"category_name": category_name})
        else:

            query = text("""
                select cat_id from category where cat_name = :category_name and sub_cat = :subcategory
            """)
            result = connection.execute(query, {"category_name": category_name, "subcategory": subcategory})
            
        cat_id_row = result.fetchone()

        if cat_id_row is None:
            raise ValueError(f"Category '{category_name}' with subcategory '{subcategory}' not found in the database.")

        cat_id = cat_id_row[0]

        query = text("""
            update expenses
            set exp_name = :expense_name,
                exp_amount = :expense_amount,
                exp_datetime = :date_of_message,
                cat_id = :cat_id
            where telegram_chat_id = :telegram_chat_id AND telegram_message_id = :telegram_message_id
        """)
        connection.execute(query, {
            "expense_name": expense_name,
            "expense_amount": expense_amount,
            "date_of_message": date_of_message,
            "cat_id": cat_id,
            "telegram_chat_id": telegram_chat_id,
            "telegram_message_id": telegram_message_id
        })

        ## to return the remaining budget for all categories
        query = text("""
            select c.cat_name, c.sub_cat, c.cat_budget - ifnull(sum(e.exp_amount), 0) as remaining_budget
            from category c
            left join expenses e on c.cat_id = e.cat_id
            group by c.cat_id
        """)
        result = connection.execute(query)
        remaining_budgets = result.fetchall()

        return remaining_budgets 

def show_budget() -> list:
    """
    Show the remaining budget for all categories.

    Returns:
        list: A list of tuples containing the category name, subcategory, and remaining budget.
    """
    with engine.begin() as connection:
        query = text("""
            select c.cat_name, c.sub_cat, c.cat_budget - ifnull(sum(e.exp_amount), 0) as remaining_budget
            from category c
            left join expenses e on c.cat_id = e.cat_id
            group by c.cat_id
        """)
        result = connection.execute(query)
        remaining_budgets = result.fetchall()

        return remaining_budgets