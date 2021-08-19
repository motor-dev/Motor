/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_PYTHONSCRIPT_SCRIPT_HH_
#define MOTOR_PYTHONLIB_PYTHONSCRIPT_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/tags/editor.script.hh>
#include <motor/script.script.hh>

namespace Motor {

class motor_api(PYTHON) PythonScript : public Script
{
    friend class PackageLoader;
published:
    PythonScript(motor_tag(EditHint::Extension(".py")) weak< const File > script);
    ~PythonScript();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
