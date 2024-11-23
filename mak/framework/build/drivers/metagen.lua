---@type Task
local task = ...

task:run_command('${PYTHON} ${METAGEN} -x c++ --std c++20 -D ${METAGEN_MACROS} --module ${METAGEN_PLUGIN} --root ${METAGEN_ROOT_NAMESPACE} --api ${METAGEN_API} --tmp ${METAGEN_TMP} ${SRC} ${METAGEN_RELATIVE_INPUT} ${METAGEN_RELATIVE_OUTPUT} ${TGT}')

return 0, task.env.METAGEN_NODES