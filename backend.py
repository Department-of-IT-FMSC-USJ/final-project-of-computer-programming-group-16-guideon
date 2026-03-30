from datetime import datetime, date
from storage import load_json, save_json, add_record

def verify_login(username, password, filename):
    """Core Authentication logic."""
    users = load_json(filename)
    for user in users:
        if user.get('username') == username and user.get('password') == password:
            return True, user
    return False, None

def check_duplicate_account(username, filename):
    """Check if account already exists."""
    users = load_json(filename)
    return any(user.get('username') == username for user in users)

def calculate_rental_price(daily_price, start_date, end_date):
    """Rental cost calculation: days x price."""
    if not isinstance(start_date, (datetime, date)) or not isinstance(end_date, (datetime, date)):
        return 0, "Invalid dates"
    
    delta = (end_date - start_date).days
    if delta <= 0:
        return daily_price, "Min. 1 day"
    
    total_amount = delta * daily_price
    return total_amount, f"Total for {delta} days: {total_amount}"

def validate_booking(jewelry_id, booking_date, filename='bookings.json'):
    """Booking validation processing."""
    if not booking_date or booking_date < date.today():
        return False, "Error: Booking date must be in the future."
    
    bookings = load_json(filename)
    for b in bookings:
        if b.get('jewelry_id') == jewelry_id and b.get('date') == str(booking_date):
            return False, "Error: Item already booked for this date."
            
    return True, "Booking valid"

def submit_booking(customer_name, contact, wedding_date, jewelry_id,
                   customer_id=None, customer_email=None, customer_address=None,
                   shop_id=None, shop_name=None, item_name=None,
                   special_notes="", fulfillment_type="", 
                   start_date=None, end_date=None, total_price=0):
    """Booking submission and storage."""
    if not customer_name or not contact or (not wedding_date and not start_date):
        return False, "Error: All fields are required."
    
    # Validation
    date_to_validate = wedding_date or start_date
    is_valid, msg = validate_booking(jewelry_id, date_to_validate)
    if not is_valid:
        return False, msg
    
    # Commission: 5% for Selling (Buy), 2% for Renting
    rate = 0.05 if fulfillment_type == "Buy" else 0.02
    commission = float(total_price) * rate

    new_booking = {
        "customer_name": customer_name,
        "customer_email": customer_email or "",
        "customer_id": customer_id or "",
        "customer_address": customer_address or "",
        "contact": contact,
        "wedding_date": str(wedding_date) if wedding_date else None,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "total_price": total_price,
        "commission": commission,
        "jewelry_id": jewelry_id,
        "item_name": item_name or "",
        "shop_id": shop_id or "",
        "shop_name": shop_name or "",
        "special_notes": special_notes or "",
        "fulfillment_type": fulfillment_type or "",
        "status": "Pending"
    }
    
    added_booking = add_record('bookings.json', new_booking)
    return True, f"✨ Reservation confirmed! (Booking ID: {added_booking['id']})"
