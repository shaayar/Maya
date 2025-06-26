"""
Utility functions for the MAYA AI Chatbot.
Contains helper functions for greetings, time formatting, and other common operations.
"""

import datetime
from typing import Optional


def get_greeting() -> str:
    """
    Get a time-appropriate greeting.
    
    Returns:
        str: A greeting appropriate for the current time of day
    """
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning!"
    elif 12 <= hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def format_time(timestamp: datetime.datetime) -> str:
    """
    Format a datetime object into a human-readable string.
    
    Args:
        timestamp: The datetime object to format
        
    Returns:
        str: Formatted time string (e.g., "3:45 PM")
    """
    return timestamp.strftime("%I:%M %p")

def format_date(date: datetime.date) -> str:
    """
    Format a date object into a human-readable string.
    
    Args:
        date: The date object to format
        
    Returns:
        str: Formatted date string (e.g., "June 25, 2025")
    """
    return date.strftime("%B %d, %Y")

def get_time_until(target_date: datetime.datetime) -> str:
    """
    Calculate and format the time until a target date.
    
    Args:
        target_date: The target date to calculate time until
        
    Returns:
        str: Formatted string showing days/hours/minutes until target
    """
    now = datetime.datetime.now()
    delta = target_date - now
    
    if delta.days > 0:
        return f"{delta.days} days"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours} hours"
    else:
        minutes = delta.seconds // 60
        return f"{minutes} minutes"

def is_overdue(due_date: Optional[str]) -> bool:
    """
    Check if a task is overdue.
    
    Args:
        due_date: ISO format date string or None
        
    Returns:
        bool: True if task is overdue, False otherwise
    """
    if not due_date:
        return False
        
    try:
        due = datetime.datetime.fromisoformat(due_date)
        now = datetime.datetime.now()
        return due < now
    except ValueError:
        return False

def get_priority_name(priority: int) -> str:
    """
    Convert a priority number to its name.
    
    Args:
        priority: Priority level (1=High, 2=Medium, 3=Low)
        
    Returns:
        str: Priority name (e.g., "High", "Medium", "Low")
    """
    priority_names = {
        1: "High",
        2: "Medium",
        3: "Low"
    }
    return priority_names.get(priority, "Medium")

def format_todo_item(todo: dict) -> str:
    """
    Format a todo item dictionary into a human-readable string.
    
    Args:
        todo: Dictionary containing todo item data
        
    Returns:
        str: Formatted todo item string
    """
    status = "✓" if todo.get("completed", False) else " "
    priority = get_priority_name(todo.get("priority", 2))
    title = todo.get("title", "Untitled")
    due = todo.get("due_date")
    category = todo.get("category")
    
    parts = [f"[{status}] {title}"]
    
    if category:
        parts.append(f"Category: {category}")
    
    if due:
        status = "Overdue" if is_overdue(due) and not todo.get("completed", False) else "Due"
        parts.append(f"{status}: {due}")
    
    return " • ".join(parts)
