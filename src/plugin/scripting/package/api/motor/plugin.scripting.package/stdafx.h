/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#if defined(building_package)
#    define MOTOR_API_PACKAGE MOTOR_EXPORT
#elif defined(motor_dll_package)
#    define MOTOR_API_PACKAGE MOTOR_IMPORT
#else
#    define MOTOR_API_PACKAGE
#endif

#ifndef MOTOR_COMPUTE
namespace Motor { namespace Arena {

minitl::Allocator& package();
minitl::Allocator& packageBuilder();

}}  // namespace Motor::Arena
#endif
