import streamlit as st
import requests
import datetime

BASE_URL = "https://myapi2-1-ye2f.onrender.com"

HEADERS = {"Authorization": f"Bearer {st.secrets['API_KEY']}"} 

st.set_page_config(page_title="F1 Grid Manager", layout="wide")
st.title("🏎️ F1 Driver Registry (SCRUD)")

# --- TABBED INTERFACE ---

tab1, tab2, tab3 = st.tabs(["View & Search", "Add Driver", "Manage Grid"])

# --- S & R: SEARCH & RETRIEVAL ---
with tab1:
    st.header("The Grid")
    search_query = st.text_input("Search by Driver Name or Country")
    
    
    response = requests.get(f"{BASE_URL}/drivers")
    if response.status_code == 200:
        drivers = response.json()
        
        # Simple Search Logic
        if search_query:
            drivers = [d for d in drivers if search_query.lower() in d['driver_name'].lower() or search_query.lower() in d['country_of_origin'].lower()]
        
        st.dataframe(drivers, use_container_width=True)
    else:
        st.error("Could not load drivers from backend.")

# --- C: CREATE ---
with tab2:
    st.header("Register New Entry")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            d_id = st.text_input("Driver ID (e.g., LewisHamilton)")
            f_name = st.text_input("First Name")
        with col2:
            l_name = st.text_input("Last Name")
            country = st.text_input("Country")

        min_date = datetime.time(1950, 1, 1)
        max_date = datetime.time.today()

        b_day = st.date_input(
            "Birthdate", 
            value=datetime.date(1995, 1, 1),
            min_value=min_date,
            max_value=max_date
        )
        
        if st.form_submit_button("Add to Grid"):
            payload = {
            "driver_name": d_id,
            "first_name": f_name,
            "last_name": l_name,
            "country_of_origin": country, # <--- Check if this comma is missing!
            "birthdate": str(b_day)       # The error happened here because of the line above
        }
            res = requests.post(f"{BASE_URL}/drivers", json=payload, headers=HEADERS)
            if res.status_code in [200, 201]:
                st.success(f"Added {f_name} successfully!")
            else:
                st.error(f"Error: {res.text}")

# --- U & D: UPDATE & DELETE ---
with tab3:
    st.header("Modify or Remove")
    target_driver = st.selectbox("Select Driver to Modify", [d['driver_name'] for d in drivers] if 'drivers' in locals() else [])
    
    col_u, col_d = st.columns(2)
    
    with col_u:
        new_country = st.text_input("Update Country")
        if st.button("Update Info"):
            # This calls your PATCH or PUT endpoint
            res = requests.patch(f"{BASE_URL}/drivers/{target_driver}", json={"country_of_origin": new_country}, headers=HEADERS)
            st.info(res.json().get("message", "Update processed"))

    with col_d:
        if st.button("🗑️ Delete Driver", type="primary"):
            res = requests.delete(f"{BASE_URL}/drivers/{target_driver}", headers=HEADERS)
            st.warning(f"Deleted {target_driver}")
