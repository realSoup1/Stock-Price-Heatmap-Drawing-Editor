import streamlit as st
import pandas as pd
import plotly.express as px

# 设置网页标题和布局（宽屏）
st.set_page_config(page_title="行业热力图编辑器", layout="wide")

st.title("📊 行业市值与涨跌幅热力图 (支持在线编辑)")

# 1. 录入你图片中的初始数据
@st.cache_data
def load_data():
    return pd.DataFrame({
        "行业名称": ["Auto", "Banks", "Capital Goods", "Commercial & Prof Services", "Consumer Discretionary", "Consumer Durables", "Consumer Services", "Consumer Staples", "Energy", "REITs", "Financial Services", "Food & Beverage", "Health Care", "Household & Personal", "Insurance", "Materials", "Media & Entertainment", "Pharma & Bio", "Real Estate", "Semiconductors", "Software", "Tech Hardware", "Telecom", "Transport", "Utilities"],
        "市值 (决定方块大小)": [1196824240128, 2019753957376, 3325999526912, 685875984384, 3533552830464, 395766622208, 1212162555904, 1365217740800, 1714321659392, 1043632927744, 5307877468672, 1369102103552, 2148172787712, 588251112448, 1101613928448, 1055719408640, 8259186911232, 3013418820608, 86151974912, 7196453345792, 6896509210624, 4620458467328, 679517208576, 749570706432, 1296555378688],
        "涨跌幅% (决定颜色)": [8.4, 3.1, -1.1, -0.2, 1.4, 8.1, 2.9, -1.5, 2.4, 2.5, 4.2, 2.5, 7.1, 2.2, 3.7, 5.4, 5.7, 3.5, -0.6, -0.5, -5.0, 8.6, 5.4, 3.5, -1.8]
    })

# 初始化数据
if "df" not in st.session_state:
    st.session_state.df = load_data()

# 把页面分成左右两列
col1, col2 = st.columns([1, 2.5])

# 左列：数据编辑器
with col1:
    st.subheader("📝 第一步：编辑数据")
    st.info("💡 提示：你可以直接点击下方表格里的数字进行修改。也可以在最底部添加新行业。右侧图表会**自动实时刷新**！")
    
    # 使用 Streamlit 自带的可交互表格组件
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic", # 允许添加或删除行
        use_container_width=True,
        hide_index=True # 隐藏前面的行号 0,1,2...
    )

# 右列：热力图展示
with col2:
    st.subheader("📈 第二步：查看热力分布图")
    
    # 确保表格里有数据再去画图，防止报错
    if not edited_df.empty:
        # 使用 Plotly 绘制矩形树图 (Treemap)
        fig = px.treemap(
            edited_df,
            path=["行业名称"], 
            values="市值 (决定方块大小)", 
            color="涨跌幅% (决定颜色)", 
            color_continuous_scale=['#32a676', '#f2f2f2', '#e93030'], # 颜色映射：绿(-)->白(0)->红(+)
            color_continuous_midpoint=0 # 强制将 0% 设为中间色（白色）
        )
        
        # 让方块上同时显示“行业名称”和“涨跌幅”
        fig.data[0].texttemplate = "<b>%{label}</b><br>%{color:.2f}%"
        
        # 调整图表边距，让它看起来更大气
        fig.update_layout(margin=dict(t=20, l=10, r=10, b=10))
        
        # 将图表展示在网页上
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("表格里没有数据啦，请添加数据！")
