function print_current_time()
    -- Get the current time formatted as a string
    local current_time = os.date("Today is %c")
    return current_time
end

return print_current_time()