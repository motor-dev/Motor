---@type Context
local context = ...
context:load_tool('internal/bolt')

Bolt.Wget = {}

context:command_driver('wget', 'cyan', '${WGET} ${WGET_OPTIONS} ${WGET_URL_F:WGET_URL} ${WGET_OUT_F:TGT[0]}')
context:command_driver('wget-status', 'cyan', '${WGET} ${WGET_OPTIONS} ${WGET_CHECK_OPTIONS} ${WGET_URL_F:WGET_URL}')

function Bolt.Wget.find_wget()
    context:try('Looking for wget', function()
        local wget
        wget = context:find_program('wget')
        if wget then
            context.env.WGET = wget
            context.env.WGET_OPTIONS = { '-q'}
            context.env.WGET_URL_F = { }
            context.env.WGET_OUT_F = { '-O' }
            context.env.WGET_CHECK_OPTIONS = { '--spider' }
            return wget:abs_path()
        end
        wget = context:find_program('curl')
        if wget then
            context.env.WGET = wget
            context.env.WGET_OPTIONS = { }
            context.env.WGET_URL_F = { '-s' }
            context.env.WGET_OUT_F = { '-o' }
            context.env.WGET_CHECK_OPTIONS = { '-I' }
            return wget:abs_path()
        end
        wget = context:find_program('pwsh')
        if not wget then
            wget = context:find_program('powershell')
        end
        if wget then
            context.env.WGET = wget
            context.env.WGET_OPTIONS = { '-Command', 'Invoke-WebRequest' }
            context.env.WGET_URL_F = { '-Uri' }
            context.env.WGET_OUT_F = { '-OutFile' }
            context.env.WGET_CHECK_OPTIONS = { '-Method', 'Head' }
            return wget:abs_path()
        end
        context:raise_error('wget not found')
    end)
end

---@param url string
---@return boolean
function Bolt.Wget.check(url)
    return context:try('Checking ' .. url, function()
        local env = context:derive()
        env.WGET_URL = url
        result, out = context:run_driver('wget-status', {}, {}, env)
        if result ~= 0 then
            context:raise_error(out)
        end
    end)
end

---@param url string
---@param output Node
---@return boolean
function Bolt.Wget.download(url, output)
    return context:try('Downloading ' .. url, function()
        local env = context:derive()
        env.WGET_URL = url
        result, out = context:run_driver('wget', {}, { output }, env)
        if result ~= 0 then
            context:raise_error(out)
        end
    end)
end
