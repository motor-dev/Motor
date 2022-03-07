/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin.scripting.python/pythonscript.meta.hh>

namespace Motor {

PythonScript::PythonScript(weak< const File > file) : Script< PythonScript >(file)
{
}

PythonScript::~PythonScript()
{
}

}  // namespace Motor
