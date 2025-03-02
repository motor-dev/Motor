---@type Task
local task = ...

local result, out, _cmd = task:run_command(
    '${PYTHON} ${METAGEN} -x c++ --std c++20 -D ${METAGEN_MACROS} --module ${METAGEN_PLUGIN} --root ${METAGEN_ROOT_NAMESPACE} --api ${METAGEN_API} --tmp ${METAGEN_TMP} ${SRC} ${METAGEN_RELATIVE_INPUT} ${METAGEN_RELATIVE_OUTPUT} ${TGT}')
return result, task.env.METAGEN_NODES, tostring(out)
