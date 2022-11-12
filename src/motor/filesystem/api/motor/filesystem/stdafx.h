/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/meta/stdafx.h>

#if defined(building_filesystem)
#    define MOTOR_API_FILESYSTEM MOTOR_EXPORT
#elif defined(motor_dll_filesystem)
#    define MOTOR_API_FILESYSTEM MOTOR_IMPORT
#else
#    define MOTOR_API_FILESYSTEM
#endif

#ifndef MOTOR_COMPUTE
namespace Motor { namespace Arena {
motor_api(FILESYSTEM) minitl::Allocator& filesystem();
}}  // namespace Motor::Arena
#endif
