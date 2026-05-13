-- Lua 插件示例

local M = {}

function M.add(a, b)
    return a + b
end

function M.greet(name)
    return "Hello from Lua, " .. name .. "!"
end

function M.run()
    return "Lua plugin loaded!"
end

return M
