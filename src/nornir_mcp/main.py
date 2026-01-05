import nornir_mcp.nornir_tools  # IMPORTANT: forces registration

from .mcp_app import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
