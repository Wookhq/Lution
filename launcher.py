# builds the command that actually starts sober

import subprocess

import paths
import envvars
import log
import sober


class LaunchError(Exception):
    pass


def sober_is_running():
    try:
        result = subprocess.run(["flatpak", "ps"], capture_output=True,
                                text=True, timeout=10,
                                env=sober.clean_env())
    except (OSError, subprocess.SubprocessError) as e:
        log.warning(f"Could not check for a running Sober ({e}), assuming none")
        return False
    if result.returncode != 0:
        return False
    return paths.SOBER_APP_ID in result.stdout


def build_sober_command(url=None):
    if sober_is_running():
        raise LaunchError(
            "Sober is already running. Close it first, otherwise it keeps the "
            "files it was started with."
        )
    args = ["flatpak", "run"]
    args += envvars.env_flatpak_args()
    args += [paths.SOBER_APP_ID]
    if url:
        args.append(url)
    return args


def launch(url=None, stdout=None, stderr=None, env=None):
    args = build_sober_command(url)
    log.info("Launching Sober")
    return subprocess.Popen(args, stdout=stdout, stderr=stderr,
                            env=sober.clean_env(env),
                            start_new_session=True)
