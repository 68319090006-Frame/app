import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. การจัดการข้อมูล (Data & Persistence) ---
# ใช้ st.session_state เพื่อจำลองฐานข้อมูลชั่วคราว (ตามโจทย์ 1.2)
if 'menu' not in st.session_state:
    st.session_state.menu = {
        'Espresso': {'price': 50, 'stock': 20},
        'Latte': {'price': 60, 'stock': 15},
        'Cappuccino': {'price': 65, 'stock': 10},
        'Green Tea': {'price': 55, 'stock': 20}
    }

if 'orders' not in st.session_state:
    st.session_state.orders = [] # เก็บประวัติออเดอร์ทั้งหมด

if 'cart' not in st.session_state:
    st.session_state.cart = [] # เก็บรายการที่กำลังเลือกปัจจุบัน

# --- 2. ฟังก์ชันระบบ (Functions) ---
def add_to_cart(item_name, quantity):
    if st.session_state.menu[item_name]['stock'] >= quantity:
        st.session_state.cart.append({'item': item_name, 'qty': quantity, 'price': st.session_state.menu[item_name]['price']})
        st.success(f"เพิ่ม {item_name} จำนวน {quantity} แก้ว เรียบร้อย")
    else:
        st.error("วัตถุดิบไม่เพียงพอ")

def process_payment():
    if not st.session_state.cart:
        st.warning("ไม่มีสินค้าในตะกร้า")
        return

    total_price = sum(item['qty'] * item['price'] for item in st.session_state.cart)
    
    # ตัดสต็อก
    for item in st.session_state.cart:
        st.session_state.menu[item['item']]['stock'] -= item['qty']
    
    # บันทึกออเดอร์ (Daily Report Data)
    order_record = {
        'time': datetime.now().strftime("%H:%M:%S"),
        'items': [item['item'] for item in st.session_state.cart],
        'total': total_price
    }
    st.session_state.orders.append(order_record)
    
    # ล้างตะกร้า
    st.session_state.cart = []
    st.success(f"ชำระเงินสำเร็จ! ยอดรวม {total_price} บาท")

# --- 3. ส่วนติดต่อผู้ใช้ (GUI Interface) ---
st.title("☕ Cafe Management System")

# แบ่งหน้าจอเป็น Tab
tab1, tab2 = st.tabs(["🛒 สั่งอาหาร (Ordering)", "📊 รายงาน & จัดการ (Management)"])

with tab1:
    st.header("รายการเมนู")
    col1, col2 = st.columns(2)
    
    # แสดงเมนูและปุ่มสั่ง
    for item, details in st.session_state.menu.items():
        with col1:
            st.write(f"**{item}** ({details['price']} บาท)")
            st.caption(f"คงเหลือ: {details['stock']}")
        with col2:
            qty = st.number_input(f"จำนวน {item}", min_value=0, max_value=10, key=f"qty_{item}")
            if st.button(f"เพิ่ม {item}", key=f"btn_{item}"):
                if qty > 0:
                    add_to_cart(item, qty)

    st.divider()
    st.subheader("ตะกร้าสินค้า")
    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart)
        total = sum(item['qty'] * item['price'] for item in st.session_state.cart)
        st.write(f"**ยอดรวมทั้งสิ้น: {total} บาท**")
        
        if st.button("💰 ยืนยันการชำระเงิน"):
            process_payment()
    else:
        st.info("ยังไม่มีสินค้าในตะกร้า")

with tab2:
    st.header("สรุปยอดขายประจำวัน")
    if st.session_state.orders:
        df_orders = pd.DataFrame(st.session_state.orders)
        st.dataframe(df_orders)
        st.metric("ยอดขายรวมวันนี้", f"{df_orders['total'].sum()} บาท")
    else:
        st.write("ยังไม่มีรายการขาย")