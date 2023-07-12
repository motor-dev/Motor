/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <motor/plugin.scripting.python/context.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <motor/plugin/plugin.hh>

#ifndef PYTHON_LIBRARY
#    error PYTHON_LIBRARY must be defined to the library name for this module
#endif

static minitl::ref< Motor::Python::Context > create(const Motor::Plugin::Context& context)
{
    using namespace Motor::Python;
    ref< PythonLibrary > library = loadPython(MOTOR_STRINGIZE(PYTHON_LIBRARY));
    if(!library)
    {
        return {};
    }
    else
    {
        return minitl::ref< Context >::create(Motor::Arena::general(), context, library);
    }
}

MOTOR_PLUGIN_REGISTER_CREATE(&create)
