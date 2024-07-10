from lupa import LuaRuntime, LuaError
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

def run_lua_in_sandbox(lua_code, safe_globals=safe_globals):
    # Load the Lua code with restricted globals
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
        return result

    except LuaError as e:
        return f"LuaError: {e}"


# Besipiels lua code
# lua_code = """
# print(math.sqrt(16))
# return "Hello from Lua"
# """

# Lua code kann ausefuehrt werden und optional kann erweiterte sandbox mit gegeben werden
#output = run_lua_in_sandbox(lua_code)

#print(output)
