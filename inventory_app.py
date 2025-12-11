"""
DME Pro Inventory System - IMPROVED AI EXTRACTION
"""

import streamlit as st
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from PIL import Image
import io
import json
import os
import time
import zipfile

# ================== CONFIGURATION ==================

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Get secrets from Streamlit Cloud
SHEET_ID = st.secrets["SHEET_ID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# ============ EXACT VALUES FROM GOOGLE SHEET DROPDOWNS ============

# Column D - Status
STATUS_OPTIONS = [
    "In Stock",
    "Out on Rental",
    "Sold"
]

# Column B - Item Name
ITEM_NAMES = [
    "Canes",
    "Commode chairs",
    "Continuous passive motion machines",
    "CPAP machines",
    "Crutches",
    "Diabetes supplies",
    "Hospital beds",
    "Infusion pumps",
    "Nebulizers",
    "Oxygen equipment",
    "Patient lifts",
    "Pressure-reducing support surfaces",
    "Suction pumps",
    "Traction equipment",
    "Walkers",
    "Wheelchairs",
    "Mobility Scooters",
    "Shower Chairs",
    "Raised Toilet Seats",
    "Grab Bars",
    "Bedside Commodes",
    "Overbed Tables",
    "Blood Pressure Monitors",
    "Glucose Meters",
    "Pulse Oximeters",
    "Reachers and Grabbers",
    "Dressing Aids",
    "Eating and Drinking Aids",
    "Alternating Pressure Pads",
    "Mattresses",
    "Lambs Wool Pads"
]

# Column C - Category
CATEGORIES = [
    "Mobility Aids",
    "Respiratory Devices",
    "Wheelchairs",
    "Bathing & Daily Living Aids",
    "Incontinence Products",
    "Hospital Beds & Accessories",
    "Patient Lifts & Slings",
    "Orthopedic Supports & Braces",
    "Diabetic Supplies",
    "Ostomy Supplies",
    "Wound Care Supplies",
    "Enteral Feeding Supplies",
    "Urological Supplies",
    "Pain Management",
    "CPAP & BiPAP Machines",
    "Nebulizers",
    "Walkers & Rollators",
    "Canes & Crutches",
    "Scooters & Power Wheelchairs",
    "Commodes & Shower Chairs",
    "Grab Bars",
    "Durable Medical Equipment (DME)",
    "Mobility"
]

# ================== AI EXTRACTION - IMPROVED ==================

def extract_equipment_data(image_bytes):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = f"""You are an expert at reading medical equipment labels and extracting data.

TASK: Carefully analyze this image of medical equipment.

IMPORTANT - READ ALL TEXT IN THE IMAGE:
1. Look for ANY serial numbers, lot numbers, or ID numbers on labels/stickers
2. Look for manufacturer/brand names (Airgas, Invacare, Drive Medical, etc.)
3. Look for model numbers
4. Count how many separate devices are in the image

SERIAL NUMBER TIPS:
- Look for labels with "SN:", "S/N:", "Serial:", "Lot:", "LOT#", "REF:"
- Check the cylinder body, tags, stickers, and any attached labels
- Oxygen cylinders often have serial numbers stamped on the neck or on tags
- Format examples: "W1063072PB01", "SN12345", "LOT-2024-001"

For item_name, choose from this EXACT list:
{json.dumps(ITEM_NAMES)}

For category, choose from this EXACT list:
{json.dumps(CATEGORIES)}

Return a JSON with ALL devices found:
{{
  "devices": [
    {{
      "item_name": "Oxygen equipment",
      "category": "Respiratory Devices",
      "serial": "THE_SERIAL_NUMBER_YOU_READ",
      "manufacturer": "THE_BRAND_NAME_YOU_READ",
      "model": "MODEL_IF_VISIBLE"
    }}
  ]
}}

CRITICAL: 
- Read the ACTUAL serial number from the image - don't leave it empty!
- If multiple devices, list each with its own serial number
- If you truly cannot read the serial, write "Not visible"

Return ONLY valid JSON."""

        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            text = text[start:end]
        
        data = json.loads(text)
        devices = data.get('devices', [data])
        
        # Validate values
        for device in devices:
            if device.get('item_name') not in ITEM_NAMES:
                device['item_name'] = ITEM_NAMES[9]  # Oxygen equipment
            if device.get('category') not in CATEGORIES:
                device['category'] = CATEGORIES[1]  # Respiratory Devices
        
        return devices
        
    except Exception as e:
        st.error(f"❌ AI Error: {str(e)}")
        return [{'item_name': ITEM_NAMES[9], 'category': CATEGORIES[1], 'serial': '', 'manufacturer': ''}]

# ================== ZIP EXTRACTION ==================

def extract_images_from_zip(zip_file):
    images = []
    try:
        zip_bytes = zip_file.read()
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as z:
            for filename in z.namelist():
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    if not filename.startswith('__MACOSX') and not filename.startswith('.'):
                        try:
                            image_bytes = z.read(filename)
                            Image.open(io.BytesIO(image_bytes))
                            images.append({'filename': os.path.basename(filename), 'bytes': image_bytes})
                        except:
                            pass
    except Exception as e:
        st.error(f"ZIP Error: {str(e)}")
    return images

# ================== GOOGLE SHEETS ==================

def get_sheets_service():
    if 'google_oauth' in st.secrets:
        try:
            creds_info = {
                'token': st.secrets['google_oauth']['token'],
                'refresh_token': st.secrets['google_oauth']['refresh_token'],
                'token_uri': st.secrets['google_oauth']['token_uri'],
                'client_id': st.secrets['google_oauth']['client_id'],
                'client_secret': st.secrets['google_oauth']['client_secret'],
                'scopes': SCOPES
            }
            creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('oauth_credentials.json'):
                st.error("❌ Missing oauth_credentials.json!")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('oauth_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('sheets', 'v4', credentials=creds)


def append_to_sheet(service, items):
    """يكتب البيانات فقط"""
    try:
        sheet = service.spreadsheets()
        
        result = sheet.values().get(spreadsheetId=SHEET_ID, range='A:A').execute()
        existing_rows = len(result.get('values', []))
        
        rows = []
        for idx, item in enumerate(items):
            item_id = f"DME-{str(existing_rows + idx).zfill(3)}"
            
            row = [
                item_id,                              # A: Item ID/SKU
                item.get('item_name', ''),            # B: Item Name
                item.get('category', ''),             # C: Category
                item.get('status', ''),               # D: Status
                '',                                   # E: Customer/Hospice Name
                '',                                   # F: Pickup Date
                None,                                 # G: Condition (dropdown)
                None,                                 # H: Available in Stock
                None,                                 # I: Location
                item.get('serial', ''),               # J: Serial/Lot Number
                '',                                   # K: Purchase Date
                '',                                   # L: Warranty Expiration
                '',                                   # M: Maintenance Due
                '',                                   # N: Condition/Status
                item.get('manufacturer', ''),         # O: Supplier Information
            ]
            rows.append(row)
        
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range='A:O',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': rows}
        ).execute()
        
        return True, len(rows)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False, 0


# ================== MAIN APP ==================

def main():
    st.set_page_config(page_title="DME Inventory", page_icon="📦", layout="wide")
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; text-align: center; margin: 0;">📦 DME Pro Inventory</h1>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📊 Sheet")
        st.markdown(f"[📄 Open Sheet](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")
        st.success("✅ Improved AI extraction!")
    
    if 'all_devices' not in st.session_state:
        st.session_state.all_devices = []
    
    # Step 1
    st.subheader("Step 1: Select Status")
    selected_status = st.selectbox("Status:", STATUS_OPTIONS)
    
    # Step 2
    st.subheader("Step 2: Upload Photos")
    uploaded_files = st.file_uploader("Choose photos or ZIP", type=['jpg', 'jpeg', 'png', 'zip'], accept_multiple_files=True)
    
    if uploaded_files:
        all_images = []
        for file in uploaded_files:
            if file.name.lower().endswith('.zip'):
                all_images.extend(extract_images_from_zip(file))
            else:
                all_images.append({'filename': file.name, 'bytes': file.getvalue()})
        
        st.success(f"✅ {len(all_images)} image(s) ready")
        
        if st.button("🔍 Extract Equipment", type="primary", use_container_width=True):
            st.session_state.all_devices = []
            progress = st.progress(0)
            status_text = st.empty()
            
            for idx, img_data in enumerate(all_images):
                status_text.text(f"🔍 Reading labels from {img_data['filename']}...")
                devices = extract_equipment_data(img_data['bytes'])
                for device in devices:
                    st.session_state.all_devices.append({
                        'filename': img_data['filename'],
                        'image_bytes': img_data['bytes'],
                        'extracted': device,
                        'status': selected_status
                    })
                progress.progress((idx + 1) / len(all_images))
            
            status_text.text("✅ Done!")
            st.rerun()
    
    # Step 3
    if st.session_state.all_devices:
        st.subheader(f"Step 3: Review {len(st.session_state.all_devices)} Device(s)")
        
        items_to_add = []
        
        for idx, data in enumerate(st.session_state.all_devices):
            serial_preview = data['extracted'].get('serial', 'No serial')[:20]
            with st.expander(f"#{idx+1}: {data['extracted'].get('item_name', 'Unknown')} | {serial_preview}", expanded=True):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(data['image_bytes'], width=150)
                
                with col2:
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        item_value = data['extracted'].get('item_name', ITEM_NAMES[0])
                        item_idx = ITEM_NAMES.index(item_value) if item_value in ITEM_NAMES else 0
                        
                        item_name = st.selectbox("Item Name:", ITEM_NAMES, index=item_idx, key=f"name_{idx}")
                        
                        serial = st.text_input(
                            "Serial/Lot Number:", 
                            value=data['extracted'].get('serial', ''), 
                            key=f"serial_{idx}",
                            help="Read from image or enter manually"
                        )
                    
                    with c2:
                        cat_value = data['extracted'].get('category', CATEGORIES[0])
                        cat_idx = CATEGORIES.index(cat_value) if cat_value in CATEGORIES else 0
                        
                        category = st.selectbox("Category:", CATEGORIES, index=cat_idx, key=f"cat_{idx}")
                        
                        manufacturer = st.text_input(
                            "Manufacturer:", 
                            value=data['extracted'].get('manufacturer', ''), 
                            key=f"mfr_{idx}"
                        )
                    
                    # Show what AI detected
                    if data['extracted'].get('serial'):
                        st.caption(f"🤖 AI detected serial: **{data['extracted'].get('serial')}**")
                    
                    items_to_add.append({
                        'item_name': item_name,
                        'category': category,
                        'status': data['status'],
                        'serial': serial,
                        'manufacturer': manufacturer
                    })
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.all_devices = []
                st.rerun()
        
        with col2:
            if st.button(f"✅ Add {len(items_to_add)} Device(s)", type="primary", use_container_width=True):
                service = get_sheets_service()
                if service:
                    success, count = append_to_sheet(service, items_to_add)
                    if success:
                        st.balloons()
                        st.success(f"🎉 Added {count} device(s)!")
                        st.session_state.all_devices = []


if __name__ == "__main__":
    main()