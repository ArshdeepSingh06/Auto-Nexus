import streamlit as st
from services.sales_service import SalesService
from services.service_module import ServiceModule
from services.inventory_service import InventoryService
from services.customer_service import CustomerService
from models.vehicle import Vehicle
from config.db_config import DBConnection

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None


# ---------- Load CSS ----------
def load_css():
    try:
        with open("assets/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("CSS file not found.")

load_css()
# ---------- Logout and Header ----------
def render_header():
    col1, col2 = st.columns([8,1])

    with col1:
        st.markdown(
            f"<h3 style='color:#00c8ff;'>AutoNexus | Role: {st.session_state.role}</h3>",
            unsafe_allow_html=True
        )

    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()

# ---------- Back to Home ----------
def back_button():
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        st.rerun()

# ---------- Auth ----------
from services.auth_service import AuthService
auth_service = AuthService()

# ---------- Login ----------
if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = auth_service.login(username, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.role = user[1]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------- RBAC I ----------
def has_access(feature):
    role = st.session_state.role

    permissions = {
        "Admin": ["ALL"],

    "Sales": [
        "Dashboard",
        "Sales",
        "Sales History",
        "Add Customer",
        "Customers",
        "View Inventory"
    ],

    "Technician": [
        "Dashboard",
        "Service Booking",
        "Service Management",
        "View Inventory"
    ]
    }

    allowed = permissions.get(role, [])

    return "ALL" in allowed or feature in allowed

# ---------- RBAC II ----------
def require_access(feature):
    if not has_access(feature):
        st.error("⛔ Access Denied")
        st.stop()

# ---------- Initialize Services ----------
sales_service = SalesService()
service_module = ServiceModule()
inventory_service = InventoryService()
customer_service = CustomerService()



# ---------- HOME ----------
if st.session_state.page == "Home":

    render_header()

    st.markdown("<h1 style='text-align:center; color:#00c8ff;'>🚗 AutoNexus</h1>", unsafe_allow_html=True)

    def nav_button(label):
        if st.button(label, use_container_width=True):
            st.session_state.page = label
            st.rerun()

    # 🔥 Define all features (order matters)
    features = [
        "Dashboard",
        "Add Vehicle",
        "View Inventory",
        "Sales",
        "Service Booking",
        "Service Management",
        "Add Customer",
        "Sales History",
        "Customers"
    ]

    # 🔥 Filter based on RBAC
    allowed_features = [f for f in features if has_access(f)]

    # 🔥 Dynamic grid (3 columns)
    cols = st.columns(3)

    for i, feature in enumerate(allowed_features):
        with cols[i % 3]:
            nav_button(feature)

choice = st.session_state.page

# ---------- Add Vehicle ----------
if choice == "Add Vehicle":
    require_access("Add Vehicle")
    render_header()
    back_button()

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

# ---------- View Inventory ----------
elif choice == "View Inventory":
    require_access("View Inventory")
    render_header()
    back_button()
    st.subheader("Vehicle Inventory")

    try:
        data = inventory_service.get_all_vehicles()

        if not data:
            st.info("No vehicles available.")
        else:
            for v in data:
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(
                        f"""
                        <div style='padding:10px; border:1px solid #333; border-radius:10px; margin-bottom:10px'>
                            <b>{v[2]} {v[3]}</b><br>
                            VIN: {v[1]}<br>
                            Price: ₹{v[4]}<br>
                            Status: {v[5]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    if st.button("🗑️ Delete", key=f"del_{v[0]}"):
                        try:
                            inventory_service.delete_vehicle(v[0])
                            st.success("Vehicle deleted!")
                            st.rerun()
                        except:
                            st.error("Cannot delete vehicle. It is linked to sales/services.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# ---------- Sales ----------
elif choice == "Sales":
    require_access("Sales")
    render_header()
    back_button()
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

            db = DBConnection()
            customers = db.fetch("SELECT id, name FROM customers")
            db.close()

            if not customers:
                st.warning("No customers found. Please add a customer first.")
            else:
                customer_options = {f"{c[0]} - {c[1]}": c[0] for c in customers}

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

# ---------- Service Book ----------
elif choice == "Service Booking":
    require_access("Service Booking")
    render_header()
    back_button()
    st.subheader("Book a Service")

    try:
        vehicles = inventory_service.get_all_vehicles()

        vehicle_options = {
            f"{v[0]} - {v[2]} {v[3]}": v[0]
            for v in vehicles
        }

        selected_vehicle = st.selectbox("Select Vehicle", list(vehicle_options.keys()))
        vehicle_id = vehicle_options[selected_vehicle]

        db = DBConnection()
        customers = db.fetch("SELECT id, name FROM customers")
        db.close()

        if not customers:
            st.warning("No customers found. Please add a customer first.")
        else:
            customer_options = {f"{c[0]} - {c[1]}": c[0] for c in customers}

            selected_customer = st.selectbox("Select Customer", list(customer_options.keys()))
            customer_id = customer_options[selected_customer]

            service_type = st.selectbox(
                "Service Type",
                ["Basic", "Standard", "Premium"]
            )

            if st.button("Book Service"):
                service_module.book_service(customer_id, vehicle_id, service_type)
                st.success("✅ Service Booked Successfully!")

    except Exception as e:
        st.error(f"Service Error: {e}")

# ---------- Service Manage ----------
elif choice == "Service Management":
    require_access("Service Management")
    render_header()
    back_button()
    st.subheader("Manage Services")

    try:
        services = service_module.get_all_services()

        if not services:
            st.info("No services found.")
        else:
            for s in services:
                col1, col2, col3 = st.columns([4, 2, 1])

                with col1:
                    st.markdown(
                        f"""
                        <div style='padding:10px; border:1px solid #333; border-radius:10px; margin-bottom:10px'>
                            Service ID: {s[0]}<br>
                            Customer ID: {s[1]}<br>
                            Vehicle ID: {s[2]}<br>
                            Type: {s[3]}<br>
                            Status: {s[4]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "In Progress", "Completed"],
                        key=f"status_{s[0]}"
                    )

                    if st.button("Update", key=f"update_{s[0]}"):
                        service_module.update_status(s[0], new_status)
                        st.success("Status updated!")
                        st.rerun()

                with col3:
                    if st.button("Delete", key=f"del_service_{s[0]}"):
                        try:
                            service_module.delete_service(s[0])
                            st.success("Service deleted!")
                            st.rerun()
                        except:
                            st.error("Delete failed.")

    except Exception as e:
        st.error(f"Error: {e}")

# ---------- Add Cust ----------
elif choice == "Add Customer":
    require_access("Add Customer")
    render_header()
    back_button()
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
                db.close()

                st.success("✅ Customer Added Successfully!")

            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Sales History ----------
elif choice == "Sales History":
    require_access("Sales History")
    render_header()
    back_button()
    st.subheader("Sales History")

    try:
        sales = sales_service.get_sales_with_details()

        if not sales:
            st.info("No sales found.")
        else:
            for s in sales:
                st.markdown(
                    f"""
                    <div style='padding:10px; border:1px solid #333; border-radius:10px; margin-bottom:10px'>
                        <b>Sale ID:</b> {s[0]}<br>
                        <b>Customer:</b> {s[1]}<br>
                        <b>Vehicle:</b> {s[2]} {s[3]}<br>
                        <b>Price:</b> ₹{s[4]}<br>
                        <b>Date:</b> {s[5]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"Error: {e}")

# ---------- Cust Management ----------
elif choice == "Customers":

    require_access("Customers")
    render_header()
    back_button()
    st.subheader("Customer Management")

    try:
        customers = customer_service.get_all_customers()

        if not customers:
            st.info("No customers found.")
        else:
            for c in customers:
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(
                        f"""
                        <div style='padding:10px; border:1px solid #333; border-radius:10px; margin-bottom:10px'>
                            <b>{c[1]}</b><br>
                            Phone: {c[2]}<br>
                            Email: {c[3]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    if st.button("🗑️ Delete", key=f"del_customer_{c[0]}"):
                        try:
                            customer_service.delete_customer(c[0])
                            st.success("Customer deleted!")
                            st.rerun()
                        except:
                            st.error("Cannot delete customer. Linked to sales/services.")

    except Exception as e:
        st.error(f"Error: {e}")

# ---------- DASHBOARD ----------
elif choice == "Dashboard":
    require_access("Dashboard")
    render_header()
    back_button()

    st.markdown("<h2 style='color:#00c8ff;'>📊 Dashboard</h2>", unsafe_allow_html=True)

    # 🔥 Fetch stats
    total_vehicles, available = inventory_service.get_vehicle_stats()
    total_sales, revenue = sales_service.get_sales_stats()
    total_services = service_module.get_service_stats()

    # 🔥 Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🚗 Vehicles", total_vehicles)
    col2.metric("✅ Available", available)
    col3.metric("💰 Sales", total_sales)
    col4.metric("🛠️ Services", total_services)

    st.markdown("---")

    st.metric("💵 Total Revenue", f"₹{revenue:,.2f}")

    st.markdown("---")

    import pandas as pd

    db = DBConnection()
    data = db.fetch("""
        SELECT DATE(date), SUM(price)
        FROM sales
        GROUP BY DATE(date)
    """)
    db.close()

    if data:
        df = pd.DataFrame(data, columns=["Date", "Revenue"])
        st.line_chart(df.set_index("Date"))
    else:
        st.info("No sales data to display.")