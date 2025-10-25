"""
Tools for the Barber Appointment Agent
These are the functions that the agent can call to perform specific tasks.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Helper function to load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Helper function to save JSON data to file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_business_info(info_type: str) -> Dict[str, Any]:
    """
    Get business information based on the requested type
    
    Args:
        info_type: Type of info requested ('hours', 'contact', 'address', 'all')
    
    Returns:
        Dictionary containing the requested business information
    """
    business_data = load_json_file('data/business_info.json')
    
    if info_type == 'hours':
        return {
            "working_hours": business_data['working_hours'],
            "detailed_hours": business_data['hours'],
            "timezone": business_data['timezone']
        }
    elif info_type == 'contact':
        return {
            "phone": business_data['phone'],
            "name": business_data['name']
        }
    elif info_type == 'address':
        return {
            "address": business_data['address'],
            "name": business_data['name']
        }
    elif info_type == 'all':
        return business_data
    else:
        return {"error": f"Unknown info type: {info_type}"}


def get_services() -> Dict[str, Any]:
    """
    Get all available services and their prices
    
    Returns:
        Dictionary containing all services with prices and durations
    """
    return load_json_file('data/services.json')


def check_availability(date: str, duration_minutes: int) -> Dict[str, Any]:
    """
    Check available time slots for a given date and duration
    
    Args:
        date: Date in YYYY-MM-DD format
        duration_minutes: Duration of the appointment in minutes
    
    Returns:
        Dictionary containing available slots and booking info
    """
    calendar_data = load_json_file('data/calendar.json')
    
    if date not in calendar_data:
        return {
            "available": False,
            "message": f"No calendar data available for {date}",
            "available_slots": []
        }
    
    day_data = calendar_data[date]
    available_slots = day_data.get('available_slots', [])
    booked_slots = day_data.get('booked_slots', [])
    
    # Filter out booked slots
    truly_available = [slot for slot in available_slots if slot not in booked_slots]
    
    # For simplicity, we'll assume all slots are 30-minute slots
    # In a real system, you'd check if consecutive slots are available for longer durations
    slot_duration = 30
    
    if duration_minutes <= slot_duration:
        # Single slot needed
        suitable_slots = truly_available
    else:
        # Multiple consecutive slots needed
        slots_needed = (duration_minutes + slot_duration - 1) // slot_duration
        suitable_slots = []
        
        for i in range(len(truly_available) - slots_needed + 1):
            consecutive_slots = truly_available[i:i + slots_needed]
            if len(consecutive_slots) == slots_needed:
                suitable_slots.append(consecutive_slots[0])  # Return start time
    
    return {
        "available": len(suitable_slots) > 0,
        "available_slots": suitable_slots,
        "duration_minutes": duration_minutes,
        "date": date,
        "message": f"Found {len(suitable_slots)} available slots for {duration_minutes} minutes"
    }


def book_appointment(
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    date: str,
    time: str,
    services: List[str],
    total_price: float,
    duration_minutes: int
) -> Dict[str, Any]:
    """
    Book an appointment and save it to the appointments file
    
    Args:
        customer_name: Full name of the customer
        customer_phone: Phone number
        customer_email: Email address
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time in HH:MM format
        services: List of service names
        total_price: Total price for all services
        duration_minutes: Total duration in minutes
    
    Returns:
        Dictionary containing booking confirmation details
    """
    # Generate unique appointment ID
    appointment_id = f"APT-{date.replace('-', '')}-{str(uuid.uuid4())[:3].upper()}"
    
    # Create appointment record
    appointment = {
        "id": appointment_id,
        "customer": {
            "name": customer_name,
            "phone": customer_phone,
            "email": customer_email
        },
        "appointment": {
            "date": date,
            "time": time,
            "services": services,
            "total_price": total_price,
            "duration_minutes": duration_minutes
        },
        "created_at": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    # Load existing appointments
    appointments = load_json_file('appointments.json')
    if not isinstance(appointments, list):
        appointments = []
    
    # Add new appointment
    appointments.append(appointment)
    
    # Save updated appointments
    save_json_file('appointments.json', appointments)
    
    # Update calendar to mark slot as booked
    calendar_data = load_json_file('data/calendar.json')
    if date in calendar_data:
        if 'booked_slots' not in calendar_data[date]:
            calendar_data[date]['booked_slots'] = []
        calendar_data[date]['booked_slots'].append(time)
        save_json_file('data/calendar.json', calendar_data)
    
    return {
        "success": True,
        "appointment_id": appointment_id,
        "appointment": appointment,
        "message": f"Appointment {appointment_id} successfully booked for {date} at {time}"
    }


def send_email_confirmation(appointment_id: str, customer_email: str) -> Dict[str, Any]:
    """
    Send email confirmation for the appointment
    This is a mock function - in a real system, you'd integrate with an email service
    
    Args:
        appointment_id: ID of the booked appointment
        customer_email: Customer's email address
    
    Returns:
        Dictionary containing email sending status
    """
    # Mock email sending - in reality, you'd use SendGrid, AWS SES, etc.
    print(f"📧 Email sent to {customer_email} for appointment {appointment_id}")
    
    return {
        "success": True,
        "message": f"Confirmation email sent to {customer_email}",
        "appointment_id": appointment_id
    }


# Tool registry - this helps the agent know what tools are available
AVAILABLE_TOOLS = {
    "get_business_info": {
        "function": get_business_info,
        "description": "Get business information (hours, contact, address, or all)",
        "parameters": {
            "info_type": "str - Type of info: 'hours', 'contact', 'address', or 'all'"
        }
    },
    "get_services": {
        "function": get_services,
        "description": "Get all available services and their prices",
        "parameters": {}
    },
    "check_availability": {
        "function": check_availability,
        "description": "Check available time slots for a given date and duration",
        "parameters": {
            "date": "str - Date in YYYY-MM-DD format",
            "duration_minutes": "int - Duration in minutes"
        }
    },
    "book_appointment": {
        "function": book_appointment,
        "description": "Book an appointment with customer details",
        "parameters": {
            "customer_name": "str - Customer's full name",
            "customer_phone": "str - Customer's phone number",
            "customer_email": "str - Customer's email address",
            "date": "str - Appointment date in YYYY-MM-DD format",
            "time": "str - Appointment time in HH:MM format",
            "services": "List[str] - List of service names",
            "total_price": "float - Total price for all services",
            "duration_minutes": "int - Total duration in minutes"
        }
    },
    "send_email_confirmation": {
        "function": send_email_confirmation,
        "description": "Send email confirmation for the appointment",
        "parameters": {
            "appointment_id": "str - ID of the booked appointment",
            "customer_email": "str - Customer's email address"
        }
    }
}
