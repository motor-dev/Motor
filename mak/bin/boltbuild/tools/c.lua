---@type Context
local context = ...

context:load_tool('compiler_core')

context:dependency_driver('c', 'green', '${CC} ${CFLAGS} ${SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${INCLUDE_ST:INCLUDES} ${DEFINE_ST:DEFINES} ${CC_SRC_FLAG:SRC} ${CC_TGT_F:TGT[0]}')
