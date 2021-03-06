/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_PYTHONSCRIPT_META_HH_
#define MOTOR_PYTHONLIB_PYTHONSCRIPT_META_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.hh>

namespace Motor {

class motor_api(PYTHON) PythonScript : public Script< PythonScript >
{
    friend class PackageLoader;
published:
    PythonScript(motor_tag(EditHint::Extension(".py")) weak< const File > script);
    ~PythonScript();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
