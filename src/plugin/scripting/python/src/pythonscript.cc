/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin.scripting.python/pythonscript.script.hh>

namespace Motor {

PythonScript::PythonScript(weak< const File > file) : Script(file)
{
}

PythonScript::~PythonScript()
{
}

}  // namespace Motor
