import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 设置网页标题和布局（宽屏）
st.set_page_config(page_title="行业热力图编辑器", layout="wide")

st.title("📊 行业市值与涨跌幅热力图")

# 1. 录入初始数据 (带缓存以提升性能)
@st.cache_data
def load_data():
    return pd.DataFrame({
        "行业名称": ["Auto", "Banks", "Capital Goods", "Commercial & Prof Services", "Consumer Discretionary", "Consumer Durables", "Consumer Services", "Consumer Staples", "Energy", "REITs", "Financial Services", "Food & Beverage", "Health Care", "Household & Personal", "Insurance", "Materials", "Media & Entertainment", "Pharma & Bio", "Real Estate", "Semiconductors", "Software", "Tech Hardware", "Telecom", "Transport", "Utilities"],
        "市值": [1196824240128, 2019753957376, 3325999526912, 685875984384, 3533552830464, 395766622208, 1212162555904, 1365217740800, 1714321659392, 1043632927744, 5307877468672, 1369102103552, 2148172787712, 588251112448, 1101613928448, 1055719408640, 8259186911232, 3013418820608, 86151974912, 7196453345792, 6896509210624, 4620458467328, 679517208576, 749570706432, 1296555378688],
        "涨跌幅%": [8.4, 3.1, -1.1, -0.2, 1.4, 8.1, 2.9, -1.5, 2.4, 2.5, 4.2, 2.5, 7.1, 2.2, 3.7, 5.4, 5.7, 3.5, -0.6, -0.5, -5.0, 8.6, 5.4, 3.5, -1.8]
    })

# 初始化数据
if "df" not in st.session_state:
    st.session_state.df = load_data()

# --- 专属粘贴框 ---
st.subheader("📋 一键导入 Excel 数据")
st.caption("使用方法：在 Excel 中选中你的三列数据（包含表头：行业名称、市值、涨跌幅%），复制后粘贴到下方框内即可。")

pasted_data = st.text_area("在此处 `Ctrl+V` 粘贴你的 Excel 数据：", height=100, placeholder="例如：\nAuto\t1196824\t8.4\nBanks\t2019753\t3.1...")

if pasted_data:
    try:
        new_df = pd.read_csv(io.StringIO(pasted_data), sep="\t")
        if len(new_df.columns) >= 3:
            # 只取前三列，防止复制了多余的空白列
            new_df = new_df.iloc[:, :3]
            new_df.columns = ["行业名称", "市值", "涨跌幅%"]
            st.session_state.df = new_df
            st.success("✨ 数据导入成功！")
        else:
            st.error("数据格式似乎不对，请确保复制了 3 列数据哦。")
    except Exception as e:
        st.error("解析数据时出现问题，请检查复制的内容格式。")

st.divider()

# 把页面分成左右两列
col1, col2 = st.columns([1, 2.5])

# 左列：数据编辑器
with col1:
    st.subheader("📝 微调数据")
    st.caption("提示：表格内的数值依然支持双击修改。")
    
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

# 右列：热力图展示
with col2:
    st.subheader("📈 行业热力分布图")
    
    if not edited_df.empty:
        # --- 核心修复：数据强制清洗，防止 % 和逗号破坏图表 ---
        plot_df = edited_df.copy()
        # 利用正则去除非数字字符（保留负号和小数点）
        plot_df["市值"] = plot_df["市值"].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        plot_df["市值"] = pd.to_numeric(plot_df["市值"], errors='coerce').fillna(0)
        
        plot_df["涨跌幅%"] = plot_df["涨跌幅%"].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        plot_df["涨跌幅%"] = pd.to_numeric(plot_df["涨跌幅%"], errors='coerce').fillna(0)
        
        # 绘制热力图
        fig = px.treemap(
            plot_df,
            path=["行业名称"], 
            values="市值", 
            color="涨跌幅%", 
            color_continuous_scale=['#00a65a', '#ffffff', '#f56954'], # 纯正红绿配色
            color_continuous_midpoint=0,
            custom_data=["涨跌幅%"] 
        )
        
        # --- 核心优化：文字自适应大小并居中 ---
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
            textposition="middle center", # 强制文字居中
            # 注意：这里删除了 textfont=dict(size=14)，让引擎自动将文字放到最大！
            marker=dict(line=dict(width=2, color='white')) # 白色切割线
        )
        
        # 优化整体布局
        fig.update_layout(
            margin=dict(t=10, l=0, r=0, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(
                title="涨跌幅(%)", 
                thickness=15, 
                len=0.8,
                bgcolor="rgba(255,255,255,0.7)"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("表格里没有数据，请添加数据！")
