/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_GL_STDAFX_H
#define MOTOR_PLUGIN_COMPUTE_OPENCL_GL_STDAFX_H

#include <motor/stdafx.h>

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin.graphics.GL4/stdafx.h>

namespace Log {

motor_api(OPENCL) weak< Logger > opencl_gl();

}

#endif
