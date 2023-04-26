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

#ifndef MOTOR_COMPUTE

namespace Motor { namespace Arena {

motor_api(WORLD) minitl::allocator& game();

}}  // namespace Motor::Arena

namespace Motor { namespace Log {

motor_api(WORLD) weak< Logger > world();

}}  // namespace Motor::Log

#endif
