/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHON_STDAFX_H
#define MOTOR_PLUGIN_SCRIPTING_PYTHON_STDAFX_H

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/stdafx.h>

#if defined(building_python)
#    define MOTOR_API_PYTHON MOTOR_EXPORT
#elif defined(motor_dll_python)
#    define MOTOR_API_PYTHON MOTOR_IMPORT
#else
#    define MOTOR_API_PYTHON
#endif

#endif
