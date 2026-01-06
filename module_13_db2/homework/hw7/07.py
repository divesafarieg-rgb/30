def hack() -> None:
    username: str = "hacker"
    password: str = "test'); DELETE FROM table_users; --"
    register(username, password)