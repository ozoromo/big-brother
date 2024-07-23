function print_current_datetime_in_germany()
    -- Get the current time in UTC
    local utc_time = os.time()

    -- Calculate the offset for CET/CEST
    -- CET (Central European Time) is UTC+1
    -- CEST (Central European Summer Time) is UTC+2
    -- This example assumes it is CET (UTC+1)
    local cet_offset = 7200  -- 1 hour in seconds

    local germany_time = utc_time + cet_offset

    local current_datetime_in_germany = os.date("%Y-%m-%d %H:%M:%S", germany_time)
    return print(current_datetime_in_germany)
end

print_current_datetime_in_germany()