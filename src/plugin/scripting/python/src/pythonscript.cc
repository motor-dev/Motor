/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin.scripting.python/pythonscript.meta.hh>

namespace Motor {

PythonScript::PythonScript(const weak< const File >& script) : Script< PythonScript >(script)
{
}

PythonScript::~PythonScript() = default;

}  // namespace Motor
