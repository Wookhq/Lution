import os
import shutil
import zipfile

from modules.config import Config

cfg = Config()


def patchApk(apk, dest):
    os.makedirs(dest, exist_ok=True)

    with zipfile.ZipFile(apk) as apkfile:
        for assetFile in apkfile.namelist():
            if not assetFile.startswith("assets/") or assetFile.endswith("/"):
                continue

            print(f"extracting {assetFile}")

            relative_path = assetFile[len("assets/") :]
            out_path = os.path.join(dest, relative_path)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            with apkfile.open(assetFile) as src, open(out_path, "wb") as dst:
                shutil.copyfileobj(src, dst)


def patch():
    if not cfg.get_row("Sober", "IsPatched"):
        print("patching")
        base_apk = os.path.expanduser(
            f"{cfg.get_row('Sober', 'Path')}/data/sober/packages/com.roblox.client/base.apk"
        )

        dest_patch = os.path.expanduser(
            f"{cfg.get_row('Sober', 'Path')}/data/sober/assets"
        )

        patchApk(base_apk, dest_patch)
        print("patching font also")

        patchFont()

        cfg.add_row("Sober", "IsPatched", True)
        cfg.save()

    else:
        print("current installation is patched")


def patchFont():
    dest_dir = os.path.expanduser(
        # "~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/content/fonts/"
        f"{cfg.get_row('Sober', 'Path')}/data/sober/asset_overlay/content/fonts"
    )
    src_dir = os.path.expanduser(
        # "~/.var/app/org.vinegarhq.Sober/data/sober/assets/content/fonts/"
        f"{cfg.get_row('Sober', 'Path')}/data/sober/assets/content/fonts"
    )

    os.makedirs(dest_dir, exist_ok=True)

    if os.path.isdir(src_dir):
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
