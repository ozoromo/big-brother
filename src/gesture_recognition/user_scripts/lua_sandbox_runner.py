from lupa import LuaRuntime, LuaError
import threading
import multiprocessing
import time
import webbrowser

# Create a Lua runtime with restricted libraries.
lua = LuaRuntime(unpack_returned_tuples=True)

def print_sandbox(input):
    print("from lua Sandbox: ", input)
    
def open_webpage(url):
    webbrowser.open(url)
    return f"{url}"

# Default sanbox only allows printing and acess to math functions
safe_globals = {
        'print': print_sandbox,  # To allow print statements from Lua to appear in Python output
        'math': lua.globals().math,  # Expose the math library
        'os': {
            'date': lua.globals().os.date  # Expose the date function from os library
        },
        'open_webpage' : open_webpage
        
    }

def lua_runner(lua_code, safe_globals, queue):
    try:
        lua_func = lua.eval("""
            function(sandbox, code)
                local env = setmetatable({}, { __index = sandbox })
                local func = load(code, nil, 't', env)
                return func()
            end
        """)
        # Execute the Lua code in the sandboxed environment
        result = lua_func(safe_globals, lua_code)
        queue.put(result)
    except LuaError as e:
        queue.put(f"LuaError: {e}")
last_script = ""
def run_lua_in_sandbox(lua_code, safe_globals=safe_globals, timeout=30):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=lua_runner, args=(lua_code, safe_globals, queue))

    process.start()
    process.join(timeout)
    global last_script
    if process.is_alive():
        process.terminate()
        process.join()
        return last_script
    else:
        if not queue.empty():
            last_script = queue.get()
        return last_script

# Besipiels lua code
# lua_code = """
# print(math.sqrt(16))
# return "Hello from Lua"
# """

# Lua code kann ausefuehrt werden und optional kann erweiterte sandbox mit gegeben werden
#output = run_lua_in_sandbox(lua_code)

#print(output)
