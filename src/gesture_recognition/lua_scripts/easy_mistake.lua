local function divide(a, b)
    if b == 0 then
        error("Division durch Null!")
    else
        return a / b
    end
end

local status, result = pcall(divide, 10, 0)
if status then
    return result
else
    return "Fehler: " .. result
end
