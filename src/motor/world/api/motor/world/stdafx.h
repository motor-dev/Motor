/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/resource/stdafx.h>
#include <motor/scheduler/stdafx.h>

#if defined(building_world)
#    define MOTOR_API_WORLD MOTOR_EXPORT
#elif defined(motor_dll_world)
#    define MOTOR_API_WORLD MOTOR_IMPORT
#else
#    define MOTOR_API_WORLD
#endif

namespace Motor { namespace Arena {

#ifndef MOTOR_COMPUTE
motor_api(WORLD) minitl::Allocator& game();
#endif

}}  // namespace Motor::Arena
