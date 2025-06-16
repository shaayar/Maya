from datetime import datetime

def get_greeting():
    """Generate a greeting with current date and time."""
    now = datetime.now()
    
    # Format the date and time
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    
    return f"Hey Shubh, it's {time_str} on {date_str}."
