---@type Context
local context = ...

if context.fun == 'configure' then
end
-- load build rules for C and C++
context:load_tool('c')
context:load_tool('cxx')

context:gcc_driver('c', 'green', '${CC} ${CFLAGS} ${CC_SRC_FLAG:SRC} ${CC_TGT_F:TGT[0]}')
context:gcc_driver('cxx', 'green', '${CXX} ${CXXFLAGS} ${CXX_SRC_FLAG:SRC} ${CXX_TGT_F:TGT[0]}')