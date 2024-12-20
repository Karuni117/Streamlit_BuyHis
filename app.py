import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# 永続化のためのCSVファイル
INVENTORY_FILE = "inventory_data.csv"

# 初期化（アプリ起動時）
if 'inventory_data' not in st.session_state:
    try:
        st.session_state.inventory_data = pd.read_csv(INVENTORY_FILE)
        st.session_state.inventory_data["Purchase Date"] = pd.to_datetime(st.session_state.inventory_data["Purchase Date"])
    except FileNotFoundError:
        st.session_state.inventory_data = pd.DataFrame(columns=["Category", "Item Name", "Quantity", "Price", "Purchase Date"])

if 'categories' not in st.session_state:
    st.session_state.categories = st.session_state.inventory_data['Category'].unique().tolist()

if 'category_examples' not in st.session_state:
    st.session_state.category_examples = {}  # カテゴリーごとの例を保存

# サイドバーのメニュー
st.sidebar.title("購入品記録")
menu = st.sidebar.radio("選択", ["Add Item", "View Inventory", "Manage Category", "Monthly", "Analyze"])

# アイテムデータの保存関数
def save_inventory_data():
    st.session_state.inventory_data.to_csv(INVENTORY_FILE, index=False)

# Add Item セクション
if menu == "Add Item":
    st.header("アイテム追加")

    # カテゴリー選択
    category = st.selectbox("カテゴリー", st.session_state.categories)

    # カテゴリーが選ばれた場合、そのカテゴリーに基づくアイテム名の例を表示
    if category and category in st.session_state.category_examples:
        st.markdown(f"**アイテム名の例:** {st.session_state.category_examples[category]}")

    # アイテム名入力
    item_name = st.text_input("アイテム名を入力")
    
    # 数量入力
    quantity = st.number_input("数量", min_value=1, step=1)
    
    # 価格入力
    price = st.number_input("価格 (円)", min_value=0, step=1)
    
    # 購入日入力
    purchase_date = st.date_input("購入日", value=datetime.date.today())

    if st.button("Add Item"):
        new_item = pd.DataFrame({
            "Category": [category],
            "Item Name": [item_name],
            "Quantity": [quantity],
            "Price": [price],
            "Purchase Date": [purchase_date]
        })
        st.session_state.inventory_data = pd.concat([st.session_state.inventory_data, new_item], ignore_index=True)
        save_inventory_data()
        st.success(f"{item_name}を追加しました！")

# Manage Category セクション
elif menu == "Manage Category":
    st.header("カテゴリー管理")
    action = st.radio("操作選択", ["カテゴリー追加", "カテゴリー削除", "現在のカテゴリー一覧表示"])

    if action == "カテゴリー追加":
        new_category = st.text_input("新しいカテゴリーを入力")
        item_name_example = st.text_input("アイテム名の例 (例: ゼブラ - サラサボールペン - ブラック - 10本)")
        
        if st.button("カテゴリー追加"):
            if new_category and item_name_example:
                if new_category not in st.session_state.categories:
                    st.session_state.categories.append(new_category)
                    st.session_state.category_examples[new_category] = item_name_example  # アイテム名の例を追加
                    save_inventory_data()
                    st.success(f"{new_category} カテゴリーが追加されました！")
                else:
                    st.warning(f"{new_category} カテゴリーは既に存在します。")
            else:
                st.error("カテゴリー名とアイテム名の例を入力してください。")

    elif action == "カテゴリー削除":
        category_to_delete = st.selectbox("削除するカテゴリーを選択", st.session_state.categories)
        if st.button("カテゴリー削除"):
            st.session_state.categories.remove(category_to_delete)
            del st.session_state.category_examples[category_to_delete]  # 例も削除
            st.session_state.inventory_data = st.session_state.inventory_data[st.session_state.inventory_data["Category"] != category_to_delete]
            save_inventory_data()
            st.success(f"{category_to_delete} カテゴリーが削除されました！")

    elif action == "現在のカテゴリー一覧表示":
        st.write("現在のカテゴリー一覧:")
        st.write(st.session_state.categories)

# View Inventory セクション
elif menu == "View Inventory":
    st.header("購入品一覧")
    view_option = st.radio("表示選択", ["All data", "カテゴリー別"])

    if view_option == "All data":
        st.write(st.session_state.inventory_data)

    elif view_option == "カテゴリー別":
        selected_category = st.selectbox("カテゴリーを選択", st.session_state.categories)
        category_data = st.session_state.inventory_data[st.session_state.inventory_data["Category"] == selected_category]
        st.write(category_data)

# Monthly セクション
elif menu == "Monthly":
    st.header("月別在庫")
    st.session_state.inventory_data["Purchase Date"] = pd.to_datetime(st.session_state.inventory_data["Purchase Date"])
    st.session_state.inventory_data["Year-Month"] = st.session_state.inventory_data["Purchase Date"].dt.to_period('M')
    
    selected_month = st.selectbox("月を選択", st.session_state.inventory_data["Year-Month"].unique())
    month_data = st.session_state.inventory_data[st.session_state.inventory_data["Year-Month"] == selected_month]

    st.write(f"{selected_month} の在庫データ:")
    st.write(month_data)

# Analyze セクション
elif menu == "Analyze":
    st.header("月別分析")
    st.session_state.inventory_data["Year-Month"] = st.session_state.inventory_data["Purchase Date"].dt.to_period('M')

    monthly_data = st.session_state.inventory_data.groupby("Year-Month").agg({"Price": "sum"}).reset_index()
    monthly_data["Year-Month"] = monthly_data["Year-Month"].astype(str)
    
    fig, ax = plt.subplots()
    ax.plot(monthly_data["Year-Month"], monthly_data["Price"], marker='o')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Price (円)')
    ax.set_title('月ごとの合計Price')
    st.pyplot(fig)
