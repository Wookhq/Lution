import streamlit as st
import json
from github import Github as auth
from modules.marketplace.downloadandinstall import MarketplaceManager
from github.GithubException import UnknownObjectException
from modules.utils.lang import LANG
from modules.utils.logging import log
from modules.config.genconfig import Config
from modules.utils.sidebar import InitSidebar

InitSidebar()
log.info("Page : Marketplace")

# work smarter, not harder
cf = Config()

authtoken = cf.Read("marketplace", "githubtoken")
if authtoken is None:
    g = auth()
else:
    g = auth(authtoken)

mm = MarketplaceManager(g)

DownloadMarketplace = mm.DownloadMarketplace
RemoveMarketplace = mm.RemoveMarketplace
ApplyMarketplace = mm.ApplyMarketplace


@st.cache_data(ttl=3600)
def GetItemCached(repo_name, item):
    try:
        repo = g.get_repo(repo_name)
        return repo.get_contents(item)
    except UnknownObjectException:
        return "Not found"


provider = cf.Read("marketplace", "marketplaceprd")
if provider is None:
    cf.Update("marketplace", "marketplaceprd", "Wookhq/Lution-Marketplace")
    st.session_state.prd = cf.Read("marketplace", "marketplaceprd")
else:
    st.session_state.prd = provider


def loadbar():
    progress = st.progress(0)
    progress.progress(10)

    avdmods = (
        GetItemCached(st.session_state.prd, "Assets/Mods/content.json") != "Not found"
    )
    progress.progress(30)

    avdthemes = (
        GetItemCached(st.session_state.prd, "Assets/Themes/content.json") != "Not found"
    )
    progress.progress(40)

    avdfflag = (
        GetItemCached(st.session_state.prd, "Assets/FastFlag/index.json") != "Not found"
    )
    progress.progress(50)

    def loadcontent(key, path, prog_value):
        if key not in st.session_state:
            content_file = GetItemCached(st.session_state.prd, path)
            if content_file != "Not found":
                st.session_state[key] = json.loads(
                    content_file.decoded_content.decode()
                )
            else:
                st.error(f"{key.upper()} NOT FOUND")
        progress.progress(prog_value)

    loadcontent("theme", "Assets/Themes/content.json", 75)
    loadcontent("mod", "Assets/Mods/content.json", 90)
    loadcontent("fflagmk", "Assets/FastFlag/index.json", 100)

    progress.empty()
    return avdmods, avdthemes, avdfflag


avdmods, avdthemes, avdfflag = loadbar()

if avdfflag and "fflagmk" in st.session_state:  # temp fix ig
    st.session_state["fflags"] = True


def ChangeProvider():
    new_provider = st.session_state.get("pr")
    if new_provider:
        cf.Update("marketplace", "marketplaceprd", new_provider)
        log.warn(f"Changed marketplace provider to: {new_provider}")


marketplace, installed, settings = st.tabs(
    [
        LANG["lution.marketplace.tab.marketplace"],
        LANG["lution.marketplace.tab.installed"],
        LANG["lution.marketplace.tab.marketplacesettings"],
    ]
)

global_index = 0


def create_columns(contents, content_type, cols_per_row=3):
    global global_index
    num_contents = len(contents)
    num_rows = (num_contents + cols_per_row - 1) // cols_per_row
    for row_num in range(num_rows):
        cols = st.columns(cols_per_row, border=True)
        for col_idx in range(cols_per_row):
            content_index = row_num * cols_per_row + col_idx
            if content_index < num_contents:
                content = contents[content_index]
                with cols[col_idx]:
                    st.markdown(f"### {content.get('title', 'Untitled')}")
                    st.markdown(
                        content.get(
                            "body",
                            LANG["lution.marketplace.marketplace.nodescprovidered"],
                        )
                    )
                    st.image(
                        content.get(
                            "image", "https://placehold.co/600x400?text=No+Image"
                        ),
                        width="stretch",
                    )
                    if "version" in content:
                        st.caption(f"WINDOWSPLAYERVERSION: {content.get('version')}")
                    if "creator" in content:
                        st.markdown(f"**By:** {content.get('creator', 'Unknown')}")
                    sb = content.get("sb")
                    if sb == "stable":
                        st.markdown(
                            LANG["lution.marketplace.marketplace.badges.stable"],
                            unsafe_allow_html=True,
                        )
                    elif sb == "unstable":
                        st.markdown(
                            LANG["lution.marketplace.marketplace.badges.unstable"],
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            LANG["lution.marketplace.marketplace.badges.unkown"],
                            unsafe_allow_html=True,
                        )
                    button_key = f"{content.get('title', 'Untitled')}_{global_index}"
                    if st.button("Download", key=button_key):
                        log.info(f"Installing {content.get('title', 'Untitled')}")
                        DownloadMarketplace(
                            content.get("title", "Untitled"), type=content_type
                        )
                    global_index += 1


fglobal_index = 0


def create_fast_flag_columns(contents, content_type, cols_per_row=3):
    global fglobal_index
    num_contents = len(contents)
    num_rows = (num_contents + cols_per_row - 1) // cols_per_row
    for row_num in range(num_rows):
        cols = st.columns(cols_per_row, border=True)
        for col_idx in range(cols_per_row):
            content_index = row_num * cols_per_row + col_idx
            if content_index < num_contents:
                content = contents[content_index]
                with cols[col_idx]:
                    st.markdown(f"### {content.get('title', 'Untitled')}")
                    st.image(
                        content.get(
                            "image", "https://placehold.co/600x400?text=No+Image"
                        ),
                        width="stretch",
                    )
                    st.write(LANG["lution.marketplace.previewfastflag"])
                    st.code(
                        content.get(
                            "preview",
                            LANG["lution.marketplace.marketplace.nodescprovidered"],
                        ),
                        language="text",
                    )

                    st.markdown(content.get("desc", "no description provided"))
                    st.markdown(
                        f'{LANG["lution.marketplace.marketplace.by"]} {content.get("by", LANG["lution.marketplace.marketplace.unkownauthor"])}'
                    )

                    button_key = f"{content.get('title', 'Untitled')}_{fglobal_index}"
                    if st.button(
                        LANG["lution.marketplace.marketplace.use"], key=button_key
                    ):
                        warnoverwrite(content.get("install"))
                    fglobal_index += 1


@st.dialog(LANG["lution.marketplace.dialog.warnoverwrite"])
def warnoverwrite(path: str):
    st.write(LANG["lution.marketplace.dialog.warnoverwritecontent"])
    if st.button(LANG["lution.marketplace.dialog.no"]):
        st.rerun()
    if st.button(LANG["lution.marketplace.dialog.yes"]):
        res = mm.get_fastflag_content(st.session_state.prd, path)
        cf.UpdateSoberConfig("fflags", {})  # nothing first

        try:
            decoded = res.decode()
            fastflag_dict = json.loads(decoded)["fastflag"]
            cf.UpdateSoberConfig("fflags", fastflag_dict)  # store as dict
            st.success(LANG["lution.marketplace.appliedfastflag"])
        except json.JSONDecodeError as e:
            st.error(f"JSON error: {e}")
            st.code(decoded)


with marketplace:
    st.header(LANG["lution.marketplace.marketplace.title"])
    st.write(LANG["lution.marketplace.marketplace.decs"])
    st.markdown("[DOCS](https://wookhq.github.io/lution/pages/docs.html)")

    # st.write(f"### {LANG['lution.marketplace.tab.themes']}")
    st.button(
        LANG["lution.marketplace.marketplace.button.reload"],
        on_click=lambda: loadbar(),
        icon="🔄",
    )
    if avdthemes and st.session_state.get("theme"):
        with st.spinner(LANG["lution.marketplace.marketplace.spinner.download"]):
            log.info("Creating Themes col")
            themeexpander = st.expander(LANG["lution.marketplace.tab.themes"])
            with themeexpander:
                create_columns(st.session_state.theme, "theme", cols_per_row=3)
    else:
        st.write(LANG["lution.marketplace.invaildprovider.theme"])

    # st.write(f"### {LANG['lution.marketplace.tab.mods']}")
    if avdmods and st.session_state.get("mod"):
        with st.spinner(LANG["lution.marketplace.marketplace.spinner.download"]):
            log.info("Creating Mods col")
            modsexpander = st.expander(LANG["lution.marketplace.tab.mods"])
            with modsexpander:
                create_columns(st.session_state.mod, "mod")
    else:
        st.write(LANG["lution.marketplace.invaildprovider.mods"])

    if avdfflag and st.session_state.get("fflags"):
        with st.spinner(LANG["lution.marketplace.marketplace.spinner.download"]):
            log.info("Creating fflag col")
            fflagsexpander = st.expander("Fast Flag")
            with fflagsexpander:
                create_fast_flag_columns(st.session_state.fflagmk, "fflag")

with installed:
    st.header(LANG["lution.marketplace.installed.title"])
    st.write(LANG["lution.marketplace.title.decs"])
    theme = cf.Read("marketplace", "InstalledThemes")
    mod = cf.Read("marketplace", "InstalledMods")
    st.write(f"### {LANG['lution.marketplace.title.decs']}")
    if theme:
        themesexpander = st.expander("Themes", expanded=True)
        with themesexpander:
            for t in theme.split(","):
                colleft1, colmid1, colright1 = st.columns(3)
                with colleft1:
                    st.markdown(f"- {t}")
                with colmid1:
                    if st.button(
                        f'{LANG["lution.marketplace.installed.apply"]} {t}',
                        use_container_width=True,
                    ):
                        with st.spinner("Applying theme..."):
                            log.info(f"Applying {t}")
                            ApplyMarketplace(t, "theme")
                with colright1:
                    if st.button(
                        f'{LANG["lution.marketplace.installed.delete"]}',
                        key=f"deletebutton_{t}",
                        use_container_width=True,
                    ):
                        log.info(f"Deleted {t}")
                        RemoveMarketplace(t, "theme")
                        del st.session_state["theme"]
                        st.rerun()

    if mod:
        modsexpander = st.expander("Mods", expanded=True)
        with modsexpander:
            for m in mod.split(","):
                colleft2, colmid2, colright2 = st.columns(3)
                with colleft2:
                    st.markdown(f"- {m}")
                with colmid2:
                    if st.button(
                        f"{LANG["lution.marketplace.installed.apply"]} {m}",
                        use_container_width=True,
                    ):
                        with st.spinner("Applying mod..."):
                            log.info(f"Applying {m}")
                            ApplyMarketplace(m, "mod")
                with colright2:
                    if st.button(
                        f'{LANG["lution.marketplace.installed.delete"]}',
                        key=f"deletebutton_{m}",
                        use_container_width=True,
                    ):
                        log.info(f"Deleted {m}")
                        RemoveMarketplace(m, "mod")
                        del st.session_state["mod"]
                        st.rerun()

with settings:
    st.header(LANG["lution.marketplace.tab.marketplacesettings"])
    st.write(LANG["lution.marketplace.marketplacesettings.changeheader"])
    st.text_input(
        LANG["lution.marketplace.marketplacesettings.provider"],
        value=st.session_state.prd,
        key="pr",
        help="e.g Username/LutionMarketplace",
    )
    st.button(
        LANG["lution.marketplace.marketplacesettings.changeprovider"],
        on_click=lambda: ChangeProvider(),
    )
