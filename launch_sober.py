# self explanatory

import sys

import launcher


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        proc = launcher.launch(url=url)
    except launcher.LaunchError as e:
        print(f"Lution: {e}")
        raise SystemExit(1)
    proc.wait()


if __name__ == "__main__":
    main()
