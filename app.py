"""
AutoNexus — Premium Automotive Admin Dashboard
app.py — Production rewrite (fully synced)
"""

import os
import streamlit as st
import pandas as pd

# ── PAGE CONFIG (must be very first Streamlit call) ────────
st.set_page_config(
    page_title="AutoNexus | Admin",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS LOADER ─────────────────────────────────────────────
def load_css() -> None:
    path = os.path.join("assets", "styles.css")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS not found at assets/styles.css")

load_css()

# ── SESSION DEFAULTS ───────────────────────────────────────
for key, val in [("page","Home"),("logged_in",False),("role",None),("user_id",None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── NAVIGATION ─────────────────────────────────────────────
def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()

# ══════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    from services.auth_service import AuthService
    auth = AuthService()

    st.markdown("""
    <div style="text-align:center;padding:3rem 0 1.5rem;">
      <div style="font-family:'Barlow Condensed',sans-serif;font-size:3rem;
        font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:#f0f4fc;">
        Auto<span style="color:#00e0ff;">Nexus</span>
      </div>
      <div style="font-size:0.72rem;letter-spacing:0.22em;text-transform:uppercase;
        color:rgba(61,79,104,1);font-family:'Barlow Condensed',sans-serif;
        margin-top:0.4rem;">
        ALL-IN-ONE CAR DASHBOARD
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([2, 2, 2])
    with mid:
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", placeholder="••••••••", type="password")
        if st.button("Sign In →", use_container_width=True):
            user = auth.login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id   = user[0]
                st.session_state.role      = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials.")

    st.stop()

# ══════════════════════════════════════════════════════════
#  RBAC
# ══════════════════════════════════════════════════════════
PERMISSIONS: dict = {
    "Admin": ["ALL"],
    "Sales": ["Dashboard","Sales","Sales History","Add Customer","Customers","View Inventory","Rental","Rental History"],
    "Technician": ["Dashboard","Service Booking","Service Management","View Inventory"],
}

def has_access(feature: str) -> bool:
    allowed = PERMISSIONS.get(st.session_state.role, [])
    return "ALL" in allowed or feature in allowed

def require_access(feature: str) -> None:
    if not has_access(feature):
        st.error("⛔ Access Denied.")
        st.stop()

# ══════════════════════════════════════════════════════════
#  SERVICES
# ══════════════════════════════════════════════════════════
from services.sales_service     import SalesService
from services.service_module    import ServiceModule
from services.inventory_service import InventoryService
from services.customer_service  import CustomerService
from models.vehicle             import Vehicle
from models.sale                import Sale
from config.db_config           import DBConnection

sales_svc = SalesService()
svc_mod   = ServiceModule()
inv_svc   = InventoryService()
cust_svc  = CustomerService()

# ══════════════════════════════════════════════════════════
#  SHARED COMPONENTS
# ══════════════════════════════════════════════════════════
def render_header() -> None:
    h1, h2 = st.columns([8, 2])
    with h1:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:12px;
              padding:0.5rem 0 1rem;border-bottom:1px solid rgba(0,224,255,0.08);
              margin-bottom:1.5rem;">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;
                font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:#f0f4fc;">
                Auto<span style='color:#00e0ff;'>Nexus</span></span>
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.66rem;
                font-weight:700;letter-spacing:0.18em;text-transform:uppercase;
                color:rgba(0,224,255,0.65);background:rgba(0,224,255,0.07);
                border:1px solid rgba(0,224,255,0.15);border-radius:100px;padding:3px 10px;">
                {st.session_state.role}</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with h2:
        st.markdown("<div style='padding-top:0.4rem;'>", unsafe_allow_html=True)
        if st.button("⏏  Logout", use_container_width=True, key="logout_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def back_button() -> None:
    if st.button("← Back", key="back_btn"):
        go("Home")


def subpage_header(title: str, icon: str = "◈") -> None:
    render_header()
    back_button()
    st.markdown(f"<h2 style='margin:0 0 1rem;'>{icon} {title}</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def info_card(body_html: str) -> None:
    st.markdown(
        f"""<div style="background:#121a2a;border:1px solid rgba(0,224,255,0.10);
          border-radius:10px;padding:14px 16px;margin-bottom:10px;
          font-size:0.88rem;color:#8898b4;line-height:1.7;">{body_html}</div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════
if st.session_state.page == "Home":
    render_header()

    st.markdown("""
    <div class="hero-wrap">
      <div class="hero-bg"></div>
      <div class="hero-overlay"></div>
      <div class="hero-status"><div class="dot"></div> SYSTEM ONLINE</div>
      <div class="hero-content">
        <div class="hero-eyebrow">Auto Dealership System</div>
        <h1 class="hero-title">Auto<span>Nexus</span></h1>
        <p class="hero-subtitle">Inventory · Sales · Services · Customers</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # FIX: unpack both values returned by get_service_stats()
    if has_access("Dashboard"):
        st.markdown('<div class="section-label">Live Metrics</div>', unsafe_allow_html=True)
        try:
            tv, av = inv_svc.get_vehicle_stats()
            ts, rev = sales_svc.get_sales_stats()
            tsvc, _completed = svc_mod.get_service_stats()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Vehicles", tv)
            m2.metric("Available", av)
            m3.metric("Sales", ts)
            m4.metric("Services", tsvc)
        except Exception as e:
            st.caption(f"Metrics unavailable: {e}")

    st.markdown('<div class="section-label">Quick Actions</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4, gap="small")

    with p1:
        st.markdown("""<div class="panel-group">
          <div class="panel-group-title">
            <span class="panel-group-icon">🚙</span> Inventory
          </div></div>""", unsafe_allow_html=True)
        if has_access("Add Vehicle"):
            if st.button("＋  Add Vehicle",    key="nav_av", use_container_width=True): go("Add Vehicle")
        if has_access("View Inventory"):
            if st.button("📋  View Inventory", key="nav_vi", use_container_width=True): go("View Inventory")
        if has_access("Rental"):
            if st.button("🚗  Rental Booking", key="nav_rb", use_container_width=True): go("Rental Booking")
        if has_access("Rental History"):
            if st.button("🕒  Rental History", key="nav_rh", use_container_width=True): go("Rental History")

    with p2:
        st.markdown("""<div class="panel-group">
          <div class="panel-group-title">
            <span class="panel-group-icon">💰</span> Sales
          </div></div>""", unsafe_allow_html=True)
        if has_access("Sales"):
            if st.button("📝  New Sale",      key="nav_s",  use_container_width=True): go("Sales")
        if has_access("Sales History"):
            if st.button("📊  Sales History", key="nav_sh", use_container_width=True): go("Sales History")

    with p3:
        st.markdown("""<div class="panel-group">
          <div class="panel-group-title">
            <span class="panel-group-icon">🔧</span> Services
          </div></div>""", unsafe_allow_html=True)
        if has_access("Service Booking"):
            if st.button("📅  Book Service",    key="nav_sb", use_container_width=True): go("Service Booking")
        if has_access("Service Management"):
            if st.button("⚙️  Manage Services", key="nav_sm", use_container_width=True): go("Service Management")

    with p4:
        st.markdown("""<div class="panel-group">
          <div class="panel-group-title">
            <span class="panel-group-icon">👤</span> Customers
          </div></div>""", unsafe_allow_html=True)
        if has_access("Add Customer"):
            if st.button("＋  Add Customer",   key="nav_ac", use_container_width=True): go("Add Customer")
        if has_access("Customers"):
            if st.button("🗂  View Customers", key="nav_vc", use_container_width=True): go("Customers")
        st.markdown('<div class="section-label">Analytics</div>', unsafe_allow_html=True)
        if has_access("Dashboard"):
            if st.button("📈 Reports", key="nav_rep", use_container_width=True):
                go("Reports")

    st.stop()

# ══════════════════════════════════════════════════════════
#  SUB-PAGES
# ══════════════════════════════════════════════════════════
page = st.session_state.page

# ── Add Vehicle ───────────────────────────────────────────
if page == "Add Vehicle":
    require_access("Add Vehicle")
    subpage_header("Add New Vehicle", "🚙")
    vin   = st.text_input("VIN")
    brand = st.text_input("Brand")
    model = st.text_input("Model")
    price = st.number_input("Price (₹)", min_value=0.0, step=1000.0)
    if st.button("Add Vehicle ✓", use_container_width=True):
        if not vin or not brand or not model:
            st.error("All fields are required.")
        else:
            try:
                inv_svc.add_vehicle(Vehicle(vin, brand, model, price))
                st.success("✅ Vehicle added!")
            except Exception as e:
                st.error(f"Error: {e}")

# ── View Inventory ────────────────────────────────────────
elif page == "View Inventory":
    require_access("View Inventory")
    subpage_header("Vehicle Inventory", "📋")
    try:
        data = inv_svc.get_all_vehicles()
        if not data:
            st.info("No vehicles found.")
        else:
            # FIX: vehicles are objects — use attributes, not tuple indices
            for v in data:
                c1, c2 = st.columns([5, 1])
                with c1:
                    sc = "#22d17a" if v.status == "Available" else "#ff5e5e"
                    info_card(
                        f"<span style='color:#f0f4fc;font-weight:600;font-size:1rem;'>{v.brand} {v.model}</span><br>"
                        f"<span style='color:rgba(61,79,104,1);font-size:0.76rem;letter-spacing:0.1em;text-transform:uppercase;'>VIN</span> {v.vin}<br>"
                        f"<span style='color:rgba(61,79,104,1);font-size:0.76rem;letter-spacing:0.1em;text-transform:uppercase;'>Price</span> ₹{v.price:,}<br>"
                        f"<span style='color:{sc};font-weight:500;'>● {v.status}</span>"
                    )
                with c2:
                    st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)
                    if st.button("🗑 Del", key=f"dv{v.id}", use_container_width=True):
                        try:
                            inv_svc.delete_vehicle(v.id)
                            st.rerun()
                        except Exception:
                            st.error("Linked to sale/service.")
                    st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")

# ── Sales ─────────────────────────────────────────────────
elif page == "Sales":
    require_access("Sales")
    subpage_header("Process Sale", "💰")
    try:
        vehicles = inv_svc.get_all_vehicles()
        vopts = {f"{v.id} — {v.brand} {v.model}": v.id for v in vehicles if v.status == "Available"}
        if not vopts:
            st.warning("No available vehicles.")
            st.stop()
        sel_v = st.selectbox("Vehicle", list(vopts.keys()))
        vehicle_id = vopts[sel_v]

        db = DBConnection()
        customers = db.fetch("SELECT id, name FROM customers")
        db.close()
        if not customers:
            st.warning("No customers — add one first.")
            st.stop()
        copts = {f"{c[0]} — {c[1]}": c[0] for c in customers}
        sel_c = st.selectbox("Customer", list(copts.keys()))
        customer_id = copts[sel_c]

        price = st.number_input("Ex-Showroom Price (₹)", min_value=0.0, step=1000.0,
                                help="Enter the base ex-showroom price. GST & cess are calculated automatically.")

        # ── Live GST Breakdown ──────────────────────────────
        if price > 0:
            gst_info = sales_svc.get_gst_breakdown(price)
            st.markdown(
                f"""<div style="background:#0d1626;border:1px solid rgba(255,181,71,0.20);
                border-radius:10px;padding:16px 20px;margin:10px 0 4px;">
                <div style="color:rgba(61,79,104,1);font-size:0.72rem;letter-spacing:0.15em;
                text-transform:uppercase;margin-bottom:10px;">
                🧾 GST Breakdown &nbsp;
                <span style="background:rgba(255,181,71,0.10);color:#ffb547;
                border:1px solid rgba(255,181,71,0.25);border-radius:100px;
                font-size:0.66rem;letter-spacing:0.08em;padding:2px 9px;">
                {gst_info['slab_label']}</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
                  <div>
                    <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Ex-Showroom</div>
                    <div style="color:#f0f4fc;font-weight:600;font-size:1rem;">₹{gst_info['ex_showroom']:,.0f}</div>
                  </div>
                  <div>
                    <div style="color:rgba(61,79,104,1);font-size:0.74rem;">GST ({gst_info['gst_rate']*100:.0f}%)</div>
                    <div style="color:#ffb547;font-weight:600;font-size:1rem;">₹{gst_info['gst_amount']:,.0f}</div>
                  </div>
                  <div>
                    <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Cess ({gst_info['cess_rate']*100:.0f}%)</div>
                    <div style="color:#ffb547;font-weight:600;font-size:1rem;">₹{gst_info['cess_amount']:,.0f}</div>
                  </div>
                  <div>
                    <div style="color:rgba(61,79,104,1);font-size:0.74rem;">On-Road Price</div>
                    <div style="color:#22d17a;font-weight:700;font-size:1.1rem;">₹{gst_info['on_road_price']:,.0f}</div>
                  </div>
                </div>
                <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.05);
                color:rgba(61,79,104,1);font-size:0.73rem;">
                Total Tax: <span style="color:#ffb547;font-weight:600;">₹{gst_info['total_tax']:,.0f}</span>
                &nbsp;·&nbsp; Effective Rate: <span style="color:#ffb547;font-weight:600;">{gst_info['effective_rate']}%</span>
                &nbsp;·&nbsp; <span style="color:rgba(61,79,104,0.7);">*Road tax / registration charges billed separately by RTO</span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

        # ── Financing toggle ────────────────────────────────
        st.markdown("---")
        st.markdown("#### 🏦 Financing")
        use_financing = st.checkbox("Customer wants to finance this purchase")

        down_payment  = 0.0
        loan_tenure   = None
        interest_rate = None
        monthly_emi   = None
        chosen_plan   = None

        if use_financing and price > 0:
            plan_labels = list(sales_svc.FINANCING_PLANS.keys())
            chosen_plan = st.selectbox("Financing Plan", plan_labels)
            tenure, rate = sales_svc.FINANCING_PLANS[chosen_plan]

            max_down = float(price)
            down_payment = st.number_input(
                "Down Payment (₹)",
                min_value=0.0,
                max_value=max_down,
                value=round(price * 0.20, 2),   # default 20%
                step=1000.0,
                help="Minimum suggested: 20% of sale price"
            )

            loan_amount = price - down_payment
            if loan_amount > 0:
                monthly_emi = sales_svc.calculate_reducing_emi(loan_amount, rate, tenure)
                total_payable = down_payment + monthly_emi * tenure
                interest_paid = total_payable - price

                st.markdown(
                    f"""<div style="background:#0d1626;border:1px solid rgba(0,224,255,0.15);
                    border-radius:10px;padding:16px 20px;margin:12px 0;">
                    <div style="color:rgba(61,79,104,1);font-size:0.72rem;letter-spacing:0.15em;
                    text-transform:uppercase;margin-bottom:10px;">Financing Summary</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                      <div>
                        <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Loan Amount</div>
                        <div style="color:#f0f4fc;font-weight:600;font-size:1rem;">₹{loan_amount:,.0f}</div>
                      </div>
                      <div>
                        <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Monthly EMI</div>
                        <div style="color:#00e0ff;font-weight:700;font-size:1.1rem;">₹{monthly_emi:,.2f}</div>
                      </div>
                      <div>
                        <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Tenure</div>
                        <div style="color:#f0f4fc;font-weight:600;font-size:1rem;">{tenure} months</div>
                      </div>
                      <div>
                        <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Interest Rate</div>
                        <div style="color:#f0f4fc;font-weight:600;">{rate*100:.0f}% p.a.</div>
                      </div>
                      <div>
                        <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Total Interest</div>
                        <div style="color:#ffb547;font-weight:600;">₹{interest_paid:,.2f}</div>
                      </div>
                      <div>
                        <div style="color:rgba(61,79,104,1);font-size:0.74rem;">Total Payable</div>
                        <div style="color:#f0f4fc;font-weight:600;">₹{total_payable:,.2f}</div>
                      </div>
                    </div></div>""",
                    unsafe_allow_html=True,
                )
                loan_tenure   = tenure
                interest_rate = rate
            else:
                st.info("Down payment covers full price — no loan required.")
                use_financing = False

        st.markdown("---")
        if st.button("Complete Sale ✓", use_container_width=True):
            if price <= 0:
                st.error("Please enter a valid sale price.")
            else:
                sale_obj = Sale(
                    vehicle_id=vehicle_id,
                    customer_id=customer_id,
                    price=price,
                    is_financed=use_financing,
                    down_payment=down_payment if use_financing else 0,
                    loan_tenure=loan_tenure,
                    interest_rate=interest_rate,
                    monthly_emi=monthly_emi,
                )
                success = sales_svc.create_sale(sale_obj)
                if success:
                    st.success("✅ Sale completed!")
                    gst_info = sales_svc.get_gst_breakdown(price)
                    if use_financing and monthly_emi:
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Ex-Showroom",   f"₹{price:,.0f}")
                        c2.metric("On-Road Price", f"₹{gst_info['on_road_price']:,.0f}")
                        c3.metric("Down Payment",  f"₹{down_payment:,.0f}")
                        c4.metric("Monthly EMI",   f"₹{monthly_emi:,.2f}")
                    else:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Ex-Showroom",   f"₹{price:,.0f}")
                        c2.metric("GST + Cess",    f"₹{gst_info['total_tax']:,.0f}")
                        c3.metric("On-Road Price", f"₹{gst_info['on_road_price']:,.0f}")
                else:
                    st.error("❌ Sale failed. Vehicle may already be sold.")
    except Exception as e:
        st.error(f"Error: {e}")

# ── Sales History ─────────────────────────────────────────
elif page == "Sales History":
    require_access("Sales History")
    subpage_header("Sales History", "📊")
    try:
        sales = sales_svc.get_sales_with_details()
        if not sales:
            st.info("No sales on record.")
        else:
            for s in sales:
                # s indices: 0=id, 1=customer, 2=brand, 3=model, 4=price, 5=date,
                #             6=is_financed, 7=down_payment, 8=loan_tenure,
                #             9=interest_rate, 10=monthly_emi
                is_fin    = len(s) > 6 and s[6]
                fin_badge = (
                    "<span style='background:rgba(0,224,255,0.10);color:#00e0ff;"
                    "border:1px solid rgba(0,224,255,0.25);border-radius:100px;"
                    "font-size:0.68rem;letter-spacing:0.1em;padding:2px 8px;"
                    "margin-left:8px;'>🏦 FINANCED</span>"
                ) if is_fin else ""

                fin_detail = ""
                if is_fin and len(s) > 10 and s[10]:
                    dp    = s[7] or 0
                    emi   = s[10]
                    mos   = s[8] or "—"
                    rate  = f"{s[9]*100:.0f}%" if s[9] else "—"
                    fin_detail = (
                        f"<br><span style='color:rgba(61,79,104,1);font-size:0.74rem;'>"
                        f"Down ₹{dp:,.0f} · EMI ₹{emi:,.2f}/mo · {mos} months @ {rate} p.a.</span>"
                    )

                c1, c2 = st.columns([5, 1])
                with c1:
                    info_card(
                        f"<span style='color:rgba(61,79,104,1);font-size:0.74rem;"
                        f"letter-spacing:0.12em;text-transform:uppercase;'>Sale #{s[0]}</span>"
                        f"{fin_badge}<br>"
                        f"<span style='color:#f0f4fc;font-weight:600;'>{s[1]}</span> · {s[2]} {s[3]}<br>"
                        f"<span style='color:#00e0ff;font-weight:600;font-size:1rem;'>₹{s[4]:,}</span>"
                        f"<span style='color:rgba(61,79,104,1);'> · {s[5]}</span>"
                        f"{fin_detail}"
                    )
                with c2:
                    st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)
                    if st.button("🗑 Del", key=f"sale_del{s[0]}", use_container_width=True):
                        success = sales_svc.delete_sale(s[0])
                        if success:
                            st.rerun()
                        else:
                            st.error("❌ Could not delete sale.")
                    st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")

# ── Service Booking ───────────────────────────────────────
elif page == "Service Booking":
    require_access("Service Booking")
    subpage_header("Book a Service", "📅")

    from models.service import Service

    try:
        vehicles = inv_svc.get_all_vehicles()
        if not vehicles:
            st.warning("No vehicles found.")
            st.stop()

        vopts = {
            f"{v.id} — {v.brand} {v.model} ({v.status})": v.id
            for v in vehicles
            if v.status in ("Available", "Sold")
        }
        if not vopts:
            st.warning("No vehicles available for servicing.")
            st.stop()
        sel_v = st.selectbox("Vehicle", list(vopts.keys()))
        vehicle_id = vopts[sel_v]

        # Auto-fetch the owner of this vehicle from the sales table
        db = DBConnection()
        owner = db.fetch("""
            SELECT c.id, c.name
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.vehicle_id = %s
            ORDER BY s.id DESC
            LIMIT 1
        """, (vehicle_id,))
        db.close()

        if not owner:
            # Vehicle not sold — fall back to Dealer
            db = DBConnection()
            dealer = db.fetch("SELECT id FROM customers WHERE name='Dealer' LIMIT 1")
            if not dealer:
                db.execute(
                    "INSERT INTO customers (name, phone, email) VALUES ('Dealer', '0000000000', 'dealer@autonexus.com')"
                )
                dealer = db.fetch("SELECT id FROM customers WHERE name='Dealer' LIMIT 1")
            db.close()
            customer_id = dealer[0][0]
            customer_name = "Dealer (Unsold Vehicle)"
        else:
            customer_id = owner[0][0]
            customer_name = owner[0][1]

        st.info(f"👤 Customer: **{customer_name}**")

        stype = st.selectbox("Service Type", ["Basic", "Standard", "Premium"])

        if st.button("Book Service ✓", use_container_width=True):
            service = Service(vehicle_id=vehicle_id, customer_id=customer_id, service_type=stype)
            success = svc_mod.book_service(service)
            if success:
                st.success(f"✅ Service booked for {customer_name}!")
            else:
                st.error("❌ Booking failed. Check logs.")

    except Exception as e:
        st.error(f"Error: {e}")

# ── Service Management ────────────────────────────────────
elif page == "Service Management":
    require_access("Service Management")
    subpage_header("Service Management", "⚙️")

    try:
        services = svc_mod.get_all_services()
        if not services:
            st.info("No services found.")
        else:
            STATUS_COLOUR = {
                "Completed":  "#22d17a",
                "In Progress": "#00e0ff",
                "Pending":    "#ff9f43",
            }
            status_list = ["Pending", "In Progress", "Completed"]

            for s in services:
                c1, c2, c3 = st.columns([4, 2, 1])

                with c1:
                    sc = STATUS_COLOUR.get(s[5], "#8898b4")
                    info_card(
                        f"<span style='color:rgba(61,79,104,1);font-size:0.74rem;"
                        f"letter-spacing:0.12em;text-transform:uppercase;'>Service #{s[0]}</span><br>"
                        f"<span style='color:#f0f4fc;font-weight:600;font-size:1rem;'>{s[2]} {s[3]}</span><br>"
                        f"Owner: <span style='color:#00e0ff;font-weight:500;'>{s[1]}</span><br>"
                        f"Type: <span style='color:#f0f4fc;font-weight:500;'>{s[4]}</span> · "
                        f"<span style='color:{sc};font-weight:500;'>● {s[5]}</span>"
                    )

                with c2:
                    current_index = status_list.index(s[5]) if s[5] in status_list else 0
                    ns = st.selectbox(
                        "Status",
                        status_list,
                        index=current_index,
                        key=f"st{s[0]}",
                        label_visibility="collapsed",
                    )
                    if st.button("Update", key=f"up{s[0]}", use_container_width=True):
                        success = svc_mod.update_status(s[0], ns)
                        if success:
                            st.success("Updated!")
                        else:
                            st.error("Update failed.")
                        st.rerun()

                with c3:
                    st.markdown("<div style='padding-top:0.25rem;'>", unsafe_allow_html=True)
                    if st.button("🗑", key=f"ds{s[0]}", use_container_width=True):
                        success = svc_mod.delete_service(s[0])
                        if success:
                            st.rerun()
                        else:
                            st.error("Delete failed.")
                    st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

# ── Add Customer ──────────────────────────────────────────
elif page == "Add Customer":
    require_access("Add Customer")
    subpage_header("Add Customer", "👤")

    name  = st.text_input("Full Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("Add Customer ✓", use_container_width=True):
        if not name or not phone or not email:
            st.error("All fields required.")
        elif not phone.isdigit() or len(phone) < 10:
            st.error("Invalid phone number.")
        elif "@" not in email:
            st.error("Invalid email.")
        else:
            try:
                db = DBConnection()
                db.execute(
                    "INSERT INTO customers (name, phone, email) VALUES (%s,%s,%s)",
                    (name.strip(), phone.strip(), email.strip()),
                )
                db.close()
                st.success("✅ Customer added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ── Customers ─────────────────────────────────────────────
elif page == "Customers":
    require_access("Customers")
    subpage_header("Customer Management", "🗂")

    try:
        customers = cust_svc.get_all_customers()
        if not customers:
            st.info("No customers found.")
        else:
            # FIX: customers are objects — use attributes, not tuple indices
            for c in customers:
                ca, cb = st.columns([5, 1])
                with ca:
                    info_card(
                        f"<span style='color:#f0f4fc;font-weight:600;font-size:1rem;'>{c.name}</span><br>"
                        f"<span style='color:rgba(61,79,104,1);font-size:0.75rem;'>📞 Phone</span> {c.phone}<br>"
                        f"<span style='color:rgba(61,79,104,1);font-size:0.75rem;'>✉ Email</span> {c.email}"
                    )
                with cb:
                    st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)
                    if st.button("🗑 Del", key=f"dc{c.id}", use_container_width=True):
                        success = cust_svc.delete_customer(c.id)
                        if success:
                            st.rerun()
                        else:
                            st.error("❌ Cannot delete (linked data exists).")
                    st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")

# ── Dashboard ─────────────────────────────────────────────
elif page == "Dashboard":
    require_access("Dashboard")
    subpage_header("Analytics Dashboard", "📊")

    try:
        tv, av = inv_svc.get_vehicle_stats()
        ts, rev = sales_svc.get_sales_stats()
        tsvc, completed = svc_mod.get_service_stats()

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Vehicles", tv)
        m2.metric("Available", av)
        m3.metric("Sales", ts)
        m4.metric("Services", tsvc, f"{completed} done")
        m5.metric("Revenue", f"₹{rev:,.0f}")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Revenue Over Time</div>', unsafe_allow_html=True)

        db = DBConnection()
        data = db.fetch("""
            SELECT DATE(date), SUM(price)
            FROM sales
            GROUP BY DATE(date)
            ORDER BY DATE(date)
        """)
        db.close()

        if data:
            df = pd.DataFrame(data, columns=["Date", "Revenue"])
            df["Date"] = pd.to_datetime(df["Date"])
            st.line_chart(df.set_index("Date"))
        else:
            st.info("No sales data to chart.")

    except Exception as e:
        st.error(f"Dashboard error: {e}")

# ── Rental Booking ────────────────────────────────────────
elif page == "Rental Booking":
    require_access("Rental")
    subpage_header("Rental Booking", "🚗")

    from services.rental_service import RentalService
    from models.rental import Rental
    rental_svc = RentalService()

    try:
        vehicles = inv_svc.get_all_vehicles()

        # Only dealer-owned (never sold) vehicles with Available status are rentable
        vopts = {}
        for v in vehicles:
            if rental_svc.is_available(v.id):
                vopts[f"{v.id} — {v.brand} {v.model} (₹{v.price:,.0f})"] = v.id

        if not vopts:
            st.warning("No dealer vehicles are currently available for rental.")
            st.caption("Only vehicles that have never been sold and are not in service can be rented.")
            st.stop()

        st.caption("Only dealer-owned (unsold) vehicles are available for rental.")
        sel_v = st.selectbox("Vehicle", list(vopts.keys()))
        vehicle_id = vopts[sel_v]

        db = DBConnection()
        customers = db.fetch("SELECT id, name FROM customers")
        db.close()
        if not customers:
            st.warning("No customers found.")
            st.stop()

        copts = {f"{c[0]} — {c[1]}": c[0] for c in customers}
        sel_c = st.selectbox("Customer", list(copts.keys()))
        customer_id = copts[sel_c]

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")

        if end_date > start_date:
            days = (end_date - start_date).days
            daily_rate = 1000
            total = days * daily_rate
            st.info(f"🧾 Duration: {days} days | Estimated Cost: ₹{total:,}")
        elif end_date == start_date:
            st.warning("⚠️ End date must be after start date.")
        else:
            st.error("❌ End date cannot be before start date.")

        if st.button("Book Rental ✓", use_container_width=True):
            if end_date <= start_date:
                st.error("End date must be after start date.")
            else:
                # FIX: pass Rental object, not raw args
                rental_obj = Rental(
                    vehicle_id=vehicle_id,
                    customer_id=customer_id,
                    start_date=start_date,
                    end_date=end_date,
                    status="Active",
                )
                success = rental_svc.book_vehicle(rental_obj)
                if success:
                    st.success("✅ Rental booked successfully!")
                else:
                    st.error("Booking failed. Vehicle may already be rented.")

    except Exception as e:
        st.error(f"Error: {e}")

# ── Reports ───────────────────────────────────────────────
elif page == "Reports":
    require_access("Dashboard")
    subpage_header("Reports", "📈")

    from services.report_service import ReportService
    report_svc = ReportService()

    try:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Monthly Revenue")
            month = st.number_input("Month", 1, 12, 1)
            year  = st.number_input("Year", 2020, 2100, 2026)
            if st.button("Get Revenue", key="rev_btn", use_container_width=True):
                revenue = report_svc.monthly_revenue(month, year)
                if revenue == 0:
                    st.info("No revenue for this period.")
                else:
                    st.success(f"₹{revenue:,.2f}")

        with col2:
            st.markdown("### Rental Income")
            start = st.date_input("From")
            end   = st.date_input("To")
            if start >= end:
                st.warning("End date must be after start date.")
            if st.button("Get Rental Income", key="rent_btn", use_container_width=True):
                if start >= end:
                    st.error("Fix date range first.")
                else:
                    income = report_svc.rental_income(start, end)
                    if income == 0:
                        st.info("No rental income in this range.")
                    else:
                        st.success(f"₹{income:,.2f}")

    except Exception as e:
        st.error(f"Error: {e}")

    # ── Financing Receivables ──────────────────────────────
    st.markdown("---")
    st.markdown("### 🏦 Financing Receivables")
    try:
        db = DBConnection()
        rows = db.fetch("""
            SELECT c.name, v.brand, v.model, s.price,
                   s.down_payment, s.loan_tenure, s.interest_rate, s.monthly_emi, s.date
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            JOIN vehicles  v ON s.vehicle_id  = v.id
            WHERE s.is_financed = 1 AND s.monthly_emi IS NOT NULL
            ORDER BY c.name
        """)
        db.close()

        if not rows:
            st.info("No financed sales on record.")
        else:
            total_outstanding = 0
            for r in rows:
                name, brand, model, price, dp, tenure, rate, emi, date = r
                total_paid    = float(dp or 0)   # down payment already collected
                total_payable = float(dp or 0) + float(emi) * int(tenure)
                outstanding   = round(total_payable - total_paid, 2)
                total_outstanding += outstanding
                info_card(
                    f"<span style='color:#f0f4fc;font-weight:600;'>{name}</span> · "
                    f"<span style='color:rgba(61,79,104,1);'>{brand} {model}</span> "
                    f"<span style='color:rgba(61,79,104,1);font-size:0.74rem;'>(sold {date})</span><br>"
                    f"<span style='color:rgba(61,79,104,1);font-size:0.74rem;'>EMI</span> "
                    f"<span style='color:#00e0ff;font-weight:600;'>₹{emi:,.0f}/mo × {tenure} months</span> "
                    f"&nbsp;·&nbsp; "
                    f"<span style='color:rgba(61,79,104,1);font-size:0.74rem;'>Down Paid</span> "
                    f"<span style='color:#22d17a;font-weight:600;'>₹{dp:,.0f}</span>"
                    f"&nbsp;·&nbsp; "
                    f"<span style='color:rgba(61,79,104,1);font-size:0.74rem;'>Total Outstanding</span> "
                    f"<span style='color:#ffb547;font-weight:600;'>₹{outstanding:,.0f}</span>"
                )
            st.markdown(
                f"<div style='text-align:right;color:#ffb547;font-weight:700;font-size:1rem;"
                f"padding:6px 4px;'>Total Receivable: ₹{total_outstanding:,.0f}</div>",
                unsafe_allow_html=True
            )
    except Exception as e:
        st.info(f"Financing data unavailable (DB may need migration): {e}")

# ── Rental History ────────────────────────────────────────
elif page == "Rental History":
    require_access("Rental History")
    subpage_header("Rental History", "📋")

    from services.rental_service import RentalService
    rental_svc = RentalService()

    try:
        db = DBConnection()
        rows = db.fetch("""
            SELECT
                r.id,
                c.name          AS customer,
                v.brand,
                v.model,
                v.vin,
                r.start_date,
                r.end_date,
                r.status,
                DATEDIFF(r.end_date, r.start_date) AS days
            FROM rentals r
            JOIN customers c ON r.customer_id = c.id
            JOIN vehicles  v ON r.vehicle_id  = v.id
            ORDER BY r.id DESC
        """)
        db.close()

        if not rows:
            st.info("No rental records found.")
        else:
            STATUS_COLOUR = {
                "Active":    "#00e0ff",
                "Completed": "#22d17a",
            }

            # ── Summary strip ──────────────────────────────
            total      = len(rows)
            active_cnt = sum(1 for r in rows if r[7] == "Active")
            done_cnt   = total - active_cnt
            s1, s2, s3 = st.columns(3)
            s1.metric("Total Rentals", total)
            s2.metric("Active",        active_cnt)
            s3.metric("Completed",     done_cnt)
            st.markdown("<hr>", unsafe_allow_html=True)

            # ── Filter ─────────────────────────────────────
            filter_status = st.selectbox(
                "Filter by status",
                ["All", "Active", "Completed"],
                key="rental_hist_filter"
            )
            filtered = rows if filter_status == "All" else [r for r in rows if r[7] == filter_status]

            if not filtered:
                st.info(f"No {filter_status.lower()} rentals.")
            else:
                for r in filtered:
                    rental_id  = r[0]
                    customer   = r[1]
                    brand      = r[2]
                    model      = r[3]
                    vin        = r[4]
                    start_date = r[5]
                    end_date   = r[6]
                    status     = r[7]
                    days       = r[8] if r[8] is not None else 0
                    cost       = days * 1000
                    sc         = STATUS_COLOUR.get(status, "#8898b4")

                    if status == "Active":
                        col_card, col_action = st.columns([5, 1])
                    else:
                        col_card = st.columns(1)[0]

                    with col_card:
                        info_card(
                            f"<span style='color:rgba(61,79,104,1);font-size:0.73rem;"
                            f"letter-spacing:0.12em;text-transform:uppercase;'>Rental #{rental_id}</span>"
                            f"<span style='float:right;color:{sc};font-weight:600;"
                            f"font-size:0.78rem;'>● {status}</span><br>"
                            f"<span style='color:#f0f4fc;font-weight:600;font-size:1rem;'>"
                            f"{brand} {model}</span> "
                            f"<span style='color:rgba(61,79,104,1);font-size:0.78rem;'>VIN: {vin}</span><br>"
                            f"<span style='color:rgba(61,79,104,1);font-size:0.75rem;'>👤 Customer</span> "
                            f"<span style='color:#f0f4fc;'>{customer}</span><br>"
                            f"<span style='color:rgba(61,79,104,1);font-size:0.75rem;'>📅 Period</span> "
                            f"<span style='color:#f0f4fc;'>{start_date} → {end_date}</span> "
                            f"<span style='color:rgba(61,79,104,1);'>({days} days)</span><br>"
                            f"<span style='color:rgba(61,79,104,1);font-size:0.75rem;'>💰 Est. Cost</span> "
                            f"<span style='color:#00e0ff;font-weight:600;'>₹{cost:,}</span>"
                        )

                    if status == "Active":
                        with col_action:
                            st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)
                            if st.button("✅ Complete", key=f"cr{rental_id}", use_container_width=True):
                                success = rental_svc.complete_rental(rental_id)
                                if success:
                                    st.success(f"Rental #{rental_id} marked complete!")
                                    st.rerun()
                                else:
                                    st.error("Could not complete rental.")
                            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading rental history: {e}")