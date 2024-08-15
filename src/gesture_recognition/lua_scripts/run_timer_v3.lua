-- Lua script

timer_name = "my_timer"  -- Declare global variable

function manage_timer()
    global result = start_timer(timer_name)  -- Call the start_timer function
    if result == "timer_started" then
        -- Timer was already started, so stop it
        return stop_timer(timer_name)
    else
        -- Timer was started successfully
        return result
    end
end

return manage_timer()  -- Execute manage_timer and return its result