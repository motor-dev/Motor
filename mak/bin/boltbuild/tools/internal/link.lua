---@type Context
local context = ...

context:command_driver('shlib', 'yellow', '${LINK} ${LINKFLAGS} ${LINKFLAGS_shlib} ${LINK_SRC_F:SRC} ${LINK_TGT_F:TGT[0]} ${LINK_LIBPATH_F:LIBPATHS} ${LINK_LIB_F:LIBS}')
context:command_driver('program', 'yellow', '${LINK} ${LINKFLAGS} ${LINKFLAGS_program} ${LINK_SRC_F:SRC} ${LIB_TGT_F:TGT[0]}')
context:command_driver('stlib', 'yellow', '${LIB} ${LIBFLAGS} ${LINK_SRC_F:SRC} ${LINK_TGT_F:TGT[0]} ${LINK_LIBPATH_F:LIBPATHS} ${LINK_LIBS_F:LIBS}')
