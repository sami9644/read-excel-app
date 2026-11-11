import requests
import uuid

# Use your key that starts with CHASECK_TEST-

CHASECK_TEST = 'CHASECK_TEST-rR3oj56cDtlEKEFNk9jUVK4wTAKZUuo3'
CHAPA_BASE_URL = "https://api.chapa.co/v1"
def initialize_payment(amount, email, tx_ref,callback_url,return_url):
    
    """Step 1: Get the checkout URL for the user"""
    url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {'Authorization': f'Bearer {CHASECK_TEST}'}
    
    payload = {
        'amount': str(amount),
        'currency': 'ETB',
        'email': email,
        'tx_ref': tx_ref,
        'callback_url': callback_url, # Replace with your URL
        'return_url': return_url,   # Replace with your URL
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()['data']['checkout_url']

def verify_payment(tx_ref):
    CHASECK_TEST = 'CHASECK_TEST-rR3oj56cDtlEKEFNk9jUVK4wTAKZUuo3'
    """Step 2: Check if the payment was actually successful"""
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {'Authorization': f'Bearer {CHASECK_TEST}'}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Check if the status is 'success' according to Chapa's API
    if data.get('status') == 'success' and data.get('data', {}).get('status') == 'success':
        return True
    return False

def settle_to_business(amount, account_number, bank_code, business_name):
    """
    Step 2: Move physical cash from your Escrow account 
    to the Bus Business bank account.
    """
    url = f"{CHAPA_BASE_URL}/transfers"
    headers = {"Authorization": f"Bearer {CHASECK_TEST}"}
    
    payload = {
        "account_name": business_name,
        "account_number": account_number,
        "amount": amount,
        "currency": "ETB",
        "bank_code": bank_code,
        "reference": f"settle-{uuid.uuid4().hex[:8]}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def get_chapa_bank_list():
    """
    Fetches the list of allowed banks from Chapa API.
    Returns a list of dictionaries containing bank names and codes.
    """
    url = "https://api.chapa.co/v1/banks"
    
    headers = {
        'Authorization': f'Bearer {CHASECK_TEST}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an error for bad status codes
        
        data = response.json()
        
        # Chapa returns a 'data' field containing the list of banks
        if data.get("message") == "Banks retrieved":
            return data.get('data', [])
        else:
            print(f"Error from Chapa: {data.get('message')}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return []
if __name__ == '__main__':
    banks = get_chapa_bank_list()
    for bank in banks:
        print(f"Name: {bank['name']} | Code: {bank['id']}")