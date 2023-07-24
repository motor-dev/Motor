/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHON_PYTHONSCRIPT_META_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHON_PYTHONSCRIPT_META_HH

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.hh>

namespace Motor {

class motor_api(PYTHON) PythonScript : public Script< PythonScript >
{
    friend class PackageLoader;

public:
    explicit PythonScript(
        [[motor::meta(EditHint::Extension(".py"))]] const weak< const File >& script);
    ~PythonScript() override;
};

}  // namespace Motor

#endif
