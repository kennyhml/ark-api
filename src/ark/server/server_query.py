from sqlite3 import Time
import a2s  # type:ignore[import]
import requests  # type:ignore[import]

from .server import Server


def query(server: Server) -> None:
    """Queries a server, sets its IP, game port, query port, and status"""
    print(f"Querying {server.name}\n{'-' * (len(server.name) + 9)}")

    result = requests.get(
        f"https://api.battlemetrics.com/servers?filter[search]={server.name}&filter[features][2e079b9a-d6f7-11e7-8461-83e84cedb373]=true&filter"
    )
    print(f"Response: {result}")
    try:
        result.raise_for_status()
    except requests.HTTPError as e:
        print(f"Fetching server failed!\n{e}")
        server.status = "?"
        return

    data = _find_relevant_data(server.name, result.json())
    if server.ip is None:
        ip = server.ip = data["attributes"]["ip"]
        print(f"Found server ip: {ip}")

    if server.game_port is None:
        game_port = server.game_port = data["attributes"]["port"]
        print(f"Found server game port: {game_port}")

    if server.query_port is None:
        query_port = server.query_port = data["attributes"]["portQuery"]
        print(f"Found server query port: {query_port}")

    _set_server_day(server)
    print(f"Server day: {server.day}")

    status = server.status = _get_server_status(server.ip, server.query_port)
    print(f"Server status: {status}\n{'-' * (len(server.name) + 9)}")


def _find_relevant_data(server_name: str, data: dict) -> dict:
    """Extracts the relevant data of a server"""
    for server_data in data["data"]:
        if server_name in server_data["attributes"]["name"]:
            return server_data
            
    raise LookupError(f"Could not find {server_name} in data {data['data']}]")


def _get_server_status(ip: str, port: str) -> str:
    """Queries a servers status by ip and port"""
    try:
        data = a2s.info((ip, port), timeout=7)
        if data:
            return "Ok"
        return "Down"
    except TimeoutError:
        return "Down"


def _set_server_day(server: Server) -> None:
    assert server.ip and server.query_port, "Can't set day without IP"
    try:
        data = a2s.rules((server.ip, server.query_port), timeout=7)
    except TimeoutError:
        print("Failed to query server rules. Server didnt respond!")
        server.status == "Down"
        return
    
    server.day = data["DayTime_s"]
