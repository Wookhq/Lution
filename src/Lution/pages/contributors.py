import streamlit as st
from modules.utils.lang import LANG
from modules.utils.contributors import contributors
from modules.utils.logging import log
from modules.utils.sidebar import InitSidebar

InitSidebar()

con = contributors()


@st.cache_data(ttl=3600)
def load_contributors():
    return con.get_contributors()


contributors_data = load_contributors()

log.info("Page : Lution contributors")
st.header(LANG["lution.tab.contributors"])

st.markdown(
    """
    Meet our fellow Contributors!    
"""
)


def render_grid(items, cols_per_row=3):
    for row_start in range(0, len(items), cols_per_row):
        row_items = items[row_start : row_start + cols_per_row]
        cols = st.columns(len(row_items), border=True)

        for col, item in zip(cols, row_items):
            with col:
                st.image(
                    item.get(
                        "avatar_url", "https://placehold.co/200x200?text=No+Avatar"
                    ),
                    width=100,
                )
                st.markdown(f"### {item.get('login', 'Unknown')}")
                bio = con.get_bio(item.get("login"))
                if bio:
                    st.markdown(bio)
                st.caption(f"Contributions: {item.get('contributions', 0)}")
                st.markdown(f"[GitHub]({item.get('html_url', '#')})")


if contributors_data:
    render_grid(contributors_data, cols_per_row=3)
else:
    st.warning("No contributors found.")
