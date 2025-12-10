"""
DME Pro Inventory System - MULTIPLE DEVICES PER IMAGE - COMPLETE
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
from datetime import datetime
import time
import zipfile

# ================== CONFIGURATION ==================

SHEET_ID = "1Gn84gSFj0Jgq-RipyVf0KHdMqWRA87lVw7868fG1v-U"
GEMINI_API_KEY = 'AIzaSyDKTBQz-hOuC4RgutCvNBCpkVFcqdzQoC4'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

STATUS_OPTIONS = ["In Stock", "Out on Rental", "Sold"]
CONDITION_OPTIONS = ["New", "Used", "Refurbished"]
CATEGORIES = [
    "Hospital Beds & Accessories", "Mobility Aids", "Respiratory Devices", "Wheelchairs",
    "Bathing & Daily Living Aids", "Patient Lifts & Slings", "Diabetic Supplies",
    "CPAP & BiPAP Machines", "Nebulizers", "Walkers & Rollators", "Canes & Crutches",
    "Scooters & Power Wheelchairs", "Commodes & Shower Chairs", "Other Medical Equipment"
]

# ================== AI EXTRACTION - MULTIPLE DEVICES ==================

def extract_equipment_data(image_bytes):
    """Extract ALL equipment from image - each device separately"""
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = """Analyze this medical equipment image carefully.

COUNT how many SEPARATE pieces of equipment are visible.
For EACH individual device, extract its unique information.

Example: If you see 3 oxygen cylinders, return 3 separate entries with their individual serial numbers.

For each device provide:
1. item_name: Type of equipment (Oxygen Cylinder, Hospital Bed, Wheelchair, etc.)
2. category: Choose from: Respiratory Devices, Hospital Beds & Accessories, Mobility Aids, Wheelchairs, Other Medical Equipment
3. serial: The UNIQUE serial/lot number for THIS specific device (look carefully at labels)
4. manufacturer: Brand name visible on THIS device
5. model: Model number if visible

Return JSON array of ALL devices:
{
  "devices": [
    {"item_name": "Oxygen Cylinder", "category": "Respiratory Devices", "serial": "W1063072PB01", "manufacturer": "Airgas", "model": "CU FT 24"},
    {"item_name": "Oxygen Cylinder", "category": "Respiratory Devices", "serial": "W1063156PB01", "manufacturer": "Airgas", "model": "CU FT 24"}
  ],
  "total_count": 2
}

IMPORTANT: Each device MUST have its own unique serial number if visible.
Return ONLY valid JSON."""

        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        # Clean JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            text = text[start:end]
        
        data = json.loads(text)
        
        if 'devices' in data:
            return data['devices']
        else:
            return [data]
        
    except Exception as e:
        st.error(f"❌ AI Error: {str(e)}")
        return [{
            'item_name': 'Unknown',
            'category': 'Other Medical Equipment',
            'serial': 'Not visible',
            'manufacturer': 'Not visible',
            'model': 'Not visible'
        }]

# ================== ZIP EXTRACTION ==================

def extract_images_from_zip(zip_file):
    """Extract images from ZIP file"""
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
                            images.append({
                                'filename': os.path.basename(filename),
                                'bytes': image_bytes
                            })
                        except:
                            pass
    except Exception as e:
        st.error(f"ZIP Error: {str(e)}")
    
    return images

# ================== GOOGLE SHEETS ==================

def get_sheets_service():
    """Get Google Sheets service using token from secrets"""
    
    # Check if we have token in Streamlit secrets (CLOUD)
    if 'google_oauth' in st.secrets:
        try:
            # Build credentials from secrets
            creds_info = {
                'token': st.secrets['google_oauth']['token'],
                'refresh_token': st.secrets['google_oauth']['refresh_token'],
                'token_uri': st.secrets['google_oauth']['token_uri'],
                'client_id': st.secrets['google_oauth']['client_id'],
                'client_secret': st.secrets['google_oauth']['client_secret'],
                'scopes': SCOPES
            }
            
            creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
            
            # Refresh if expired
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            return build('sheets', 'v4', credentials=creds)
            
        except Exception as e:
            st.error(f"Error loading credentials from secrets: {e}")
            st.stop()
    
    # Fallback to local OAuth (for local development)
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('oauth_credentials.json'):
                st.error("❌ Missing oauth_credentials.json file!")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('oauth_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('sheets', 'v4', credentials=creds)

# ================== MAIN APP ==================

def main():
    st.set_page_config(page_title="DME Inventory", page_icon="📦", layout="wide")
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; text-align: center; margin: 0;">📦 DME Pro Inventory System</h1>
        <p style="color: white; text-align: center; margin: 5px 0 0 0;">Detects multiple devices per image!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Sheet Info")
        st.markdown(f"[📄 Open Google Sheet](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")
        
        st.header("📋 Status Options")
        for status in STATUS_OPTIONS:
            st.write(f"• {status}")
        
        st.header("🔍 Features")
        st.write("✅ Detects multiple devices")
        st.write("✅ Each device = separate row")
        st.write("✅ Auto Item ID (DME-XXX)")
        st.write("✅ ZIP file support")
    
    # Initialize session state
    if 'all_devices' not in st.session_state:
        st.session_state.all_devices = []
    
    # Step 1: Status
    st.subheader("Step 1: Select Status")
    selected_status = st.selectbox("Equipment Status:", STATUS_OPTIONS)
    
    # Step 2: Upload
    st.subheader("Step 2: Upload Photos or ZIP")
    uploaded_files = st.file_uploader(
        "Choose photos or ZIP file",
        type=['jpg', 'jpeg', 'png', 'zip'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        all_images = []
        
        for file in uploaded_files:
            if file.name.lower().endswith('.zip'):
                st.info(f"📦 Extracting from {file.name}...")
                zip_images = extract_images_from_zip(file)
                st.success(f"Found {len(zip_images)} images in ZIP")
                all_images.extend(zip_images)
            else:
                all_images.append({
                    'filename': file.name,
                    'bytes': file.getvalue()
                })
        
        st.success(f"✅ {len(all_images)} image(s) ready")
        
        # Show thumbnails
        if all_images:
            cols = st.columns(min(len(all_images), 6))
            for idx, img in enumerate(all_images[:6]):
                with cols[idx]:
                    st.image(img['bytes'], width=80)
            if len(all_images) > 6:
                st.caption(f"... and {len(all_images) - 6} more")
        
        # Extract button
        if st.button("🔍 Extract ALL Equipment", type="primary", use_container_width=True):
            st.session_state.all_devices = []
            
            progress = st.progress(0)
            status_text = st.empty()
            total_devices = 0
            
            for idx, img_data in enumerate(all_images):
                status_text.text(f"Processing {img_data['filename']}... ({idx+1}/{len(all_images)})")
                
                # Get ALL devices from this image
                devices = extract_equipment_data(img_data['bytes'])
                
                for device in devices:
                    st.session_state.all_devices.append({
                        'filename': img_data['filename'],
                        'image_bytes': img_data['bytes'],
                        'extracted': device,
                        'status': selected_status
                    })
                    total_devices += 1
                
                progress.progress((idx + 1) / len(all_images))
                time.sleep(0.3)
            
            status_text.text(f"✅ Found {total_devices} total devices from {len(all_images)} images!")
            st.rerun()
    
    # Step 3: Review & Add
    if st.session_state.all_devices:
        st.subheader(f"Step 3: Review {len(st.session_state.all_devices)} Device(s)")
        
        items_to_add = []
        
        for idx, data in enumerate(st.session_state.all_devices):
            serial_display = data['extracted'].get('serial', 'N/A')[:20]
            
            with st.expander(f"📸 #{idx+1}: {data['extracted'].get('item_name', 'Unknown')} | Serial: {serial_display}", expanded=True):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(data['image_bytes'], width=120)
                    st.caption(f"From: {data['filename']}")
                
                with col2:
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        item_name = st.text_input(
                            "Item Name:", 
                            value=data['extracted'].get('item_name', ''), 
                            key=f"name_{idx}"
                        )
                        serial = st.text_input(
                            "Serial Number:", 
                            value=data['extracted'].get('serial', ''), 
                            key=f"serial_{idx}"
                        )
                        manufacturer = st.text_input(
                            "Manufacturer:", 
                            value=data['extracted'].get('manufacturer', ''), 
                            key=f"mfr_{idx}"
                        )
                    
                    with c2:
                        # Find matching category
                        cat_value = data['extracted'].get('category', 'Other Medical Equipment')
                        cat_idx = len(CATEGORIES) - 1
                        for i, cat in enumerate(CATEGORIES):
                            if cat.lower() in cat_value.lower() or cat_value.lower() in cat.lower():
                                cat_idx = i
                                break
                        
                        category = st.selectbox(
                            "Category:", 
                            CATEGORIES, 
                            index=cat_idx, 
                            key=f"cat_{idx}"
                        )
                        condition = st.selectbox(
                            "Condition:", 
                            [""] + CONDITION_OPTIONS, 
                            key=f"cond_{idx}"
                        )
                        location = st.text_input(
                            "Location:", 
                            key=f"loc_{idx}"
                        )
                    
                    notes = st.text_input("Notes:", key=f"notes_{idx}")
                    st.caption(f"Status: **{data['status']}** | Will get ID: **DME-{str(idx+1).zfill(3)}**")
                    
                    items_to_add.append({
                        'item_name': item_name,
                        'category': category,
                        'status': data['status'],
                        'serial': serial,
                        'manufacturer': manufacturer,
                        'condition': condition,
                        'location': location,
                        'notes': notes
                    })
        
        st.divider()
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Devices", len(items_to_add))
        with col2:
            st.metric("Status", selected_status)
        with col3:
            st.metric("ID Range", f"DME-001 → DME-{len(items_to_add):03d}")
        
        # Buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.all_devices = []
                st.rerun()
        
        with col_btn2:
            if st.button(f"✅ Add {len(items_to_add)} Device(s) to Google Sheets", type="primary", use_container_width=True):
                with st.spinner("Adding to inventory..."):
                    service = get_sheets_service()
                    if service:
                        success, count = append_to_sheet(service, items_to_add)
                        if success:
                            st.balloons()
                            st.success(f"🎉 Successfully added {count} device(s) to inventory!")
                            st.markdown(f"[📊 View Google Sheet](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")
                            st.session_state.all_devices = []
                        else:
                            st.error("Failed to add to sheet. Check error above.")
                    else:
                        st.error("Could not connect to Google Sheets. Check oauth_credentials.json")

if __name__ == "__main__":
    main()