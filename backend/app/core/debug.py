def debug_log(msg):
    with open("app_debug.log", "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")
