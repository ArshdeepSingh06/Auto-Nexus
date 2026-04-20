import streamlit as st
from services.sales_service import SalesService
from services.service_module import ServiceModule
from services.inventory_service import InventoryService
from models.vehicle import Vehicle
from config.db_config import DBConnection

# ---------- Load CSS ----------
def load_css():
    try:
        with open("assets/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("CSS file not found.")

load_css()

# ---------- Initialize Services ----------
sales_service = SalesService()
service_module = ServiceModule()
inventory_service = InventoryService()

# ---------- UI Header ----------
st.title("🚗 AutoNexus Dashboard")

menu = ["Add Vehicle", "Add Customer", "View Inventory", "Sales", "Service Booking"]
choice = st.sidebar.selectbox("Menu", menu)

# =========================================================
# ADD VEHICLE
# =========================================================
if choice == "Add Vehicle":
    st.subheader("Add New Vehicle")

    vin = st.text_input("VIN")
    brand = st.text_input("Brand")
    model = st.text_input("Model")
    price = st.number_input("Price", min_value=0.0)

    if st.button("Add Vehicle"):
        if not vin or not brand or not model:
            st.error("All fields are required.")
        else:
            try:
                vehicle = Vehicle(vin, brand, model, price)
                inventory_service.add_vehicle(vehicle)
                st.success("✅ Vehicle Added Successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

# =========================================================
# VIEW INVENTORY
# =========================================================
elif choice == "View Inventory":
    st.subheader("Vehicle Inventory")

    try:
        data = inventory_service.get_all_vehicles()

        if not data:
            st.info("No vehicles available.")
        else:
            for v in data:
                st.markdown(
                    f"""
                    <div style='padding:10px; border:1px solid #333; border-radius:10px; margin-bottom:10px'>
                        <b>{v[2]} {v[3]}</b><br>
                        Price: ₹{v[4]}<br>
                        Status: {v[5]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# =========================================================
# SALES MODULE
# =========================================================
elif choice == "Sales":
    st.subheader("Process Sale")

    try:
        vehicles = inventory_service.get_all_vehicles()

        vehicle_options = {
            f"{v[0]} - {v[2]} {v[3]}": v[0]
            for v in vehicles if v[5] == "Available"
        }

        if not vehicle_options:
            st.warning("No available vehicles.")
        else:
            selected_vehicle = st.selectbox("Select Vehicle", list(vehicle_options.keys()))
            vehicle_id = vehicle_options[selected_vehicle]

            # 🔥 FETCH CUSTOMERS FROM DB
            db = DBConnection()
            customers = db.fetch("SELECT id, name FROM customers")

            if not customers:
                st.warning("No customers found. Please add a customer first.")
            else:
                customer_options = {
                    f"{c[0]} - {c[1]}": c[0]
                    for c in customers
                }

                selected_customer = st.selectbox("Select Customer", list(customer_options.keys()))
                customer_id = customer_options[selected_customer]

                price = st.number_input("Final Price", min_value=0.0)

                if st.button("Complete Sale"):
                    total = sales_service.calculate_total(price)
                    emi = sales_service.calculate_emi(price)

                    sales_service.create_sale(vehicle_id, customer_id, price)

                    st.success("✅ Sale Completed!")
                    st.info(f"Total (with GST): ₹{total:.2f}")
                    st.info(f"EMI (12 months): ₹{emi:.2f}/month")

    except Exception as e:
        st.error(f"Sales Error: {e}")

elif choice == "Service Booking":
    st.subheader("Book a Service")

    try:
        vehicles = inventory_service.get_all_vehicles()

        vehicle_options = {
            f"{v[0]} - {v[2]} {v[3]}": v[0]
            for v in vehicles
        }

        selected_vehicle = st.selectbox("Select Vehicle", list(vehicle_options.keys()))
        vehicle_id = vehicle_options[selected_vehicle]

        customer_id = st.number_input("Customer ID", min_value=1)

        service_type = st.selectbox(
            "Service Type",
            ["Basic", "Standard", "Premium"]
        )

        if st.button("Book Service"):
            service_module.book_service(customer_id, vehicle_id, service_type)
            st.success("✅ Service Booked Successfully!")

    except Exception as e:
        st.error(f"Service Error: {e}")
elif choice == "Add Customer":
    st.subheader("Add New Customer")

    name = st.text_input("Customer Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("Add Customer"):
        if not name or not phone or not email:
            st.error("All fields are required.")
        else:
            try:
                db = DBConnection()

                query = "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)"
                db.execute(query, (name, phone, email))

                st.success("✅ Customer Added Successfully!")

            except Exception as e:
                st.error(f"Error: {e}")