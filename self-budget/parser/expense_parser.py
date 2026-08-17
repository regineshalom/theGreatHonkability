## Parse the telegram text to extract expense informations

from decimal import Decimal, InvalidOperation

from sqlalchemy import text
from textwrap import dedent

def parse_tele_text(text: str) -> tuple:
    """
    Parse the text of a Telegram message to extract expense information.

    Args:
        text (str): The text of the Telegram message.

    Returns:
        tuple: A tuple containing the expense name, amount, category name, and subcategory.
    """
    parts = text.split('-')
    if len(parts) < 3:
        raise ValueError(dedent("""
                for your goldfish memory, the expected format:
                <i>'expense name - amount - category name - subcategory'</i>

                following categories made:
                - food
                - public transportation
                - tardiness
                - whimsies

                following subcategories made:
                - food: lunch, dinner, coffee
                - tardiness: tada, grab, gojek
                - whimsies: clothes, misc (your horrible tendency to buy dumb stuff)
            """).strip())

    expName = parts[0].strip().lower()
    catName = parts[2].strip().lower()
    subCat = parts[3].strip().lower() if len(parts) > 3 else None

    if catName not in ["food", "public transportation", "tardiness", "whimsies"]:
        raise ValueError(dedent(f"""wat is this: {catName} ,, follow this list leh.
        
        categories made:
        - food
        - public transportation
        - tardiness
        - whimsies
        """)
        )
    
    try:
        expAmount = Decimal(parts[1].strip())
    
        if expAmount.as_tuple().exponent < -2:
            raise ValueError(f"woi sg cents don't have more than 2 decimal places lah: {expAmount}")

        expAmount = int(expAmount * 100)  # Convert to cents for storage in the database
        
    except InvalidOperation:
        raise ValueError(f"udk wht number is ah: {expAmount} ,, record how much u spent pls")
    
    return expName, expAmount, catName, subCat