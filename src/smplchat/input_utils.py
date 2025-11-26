"""start input helper, could be in some misc or utils folder too"""
from smplchat import settings


def parse_host_port(s: str) -> tuple[str, int]:
    """Parse host:port or host."""
    if ":" in s:
        host, port_s = s.rsplit(":", 1)
        return host, int(port_s)
    return s, settings.PORT

def parse_partners(partners_str):
    """Parse list of host ports, using parse_host_port. For tui.py."""
    peers = []
    if not partners_str:
        return peers

    for item in partners_str.split(","):
        item = item.strip()
        if not item:
            continue
        peers.append(parse_host_port(item))

    return peers

def prompt_nick() -> str:
    """Prompts nickname at start."""
    input_nick = input("Enter nickname for chat: ").strip()
    return input_nick or "anon"

def prompt_self_addr(
    default_host="127.0.0.1",
    default_port=None,
) -> tuple[str, int]:
    """Prompts host:port at start."""
    if default_port is None:
        default_port = settings.PORT

    default_str = f"{default_host}:{default_port}"
    print(f"Enter your own address as ip:port (leave empty for default {default_str})")
    addr_in = input("Your address: ").strip()

    if not addr_in:
        return (default_host, default_port)

    return parse_host_port(addr_in)
