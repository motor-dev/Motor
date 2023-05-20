/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/kernel/colors.hh>
#include <motor/kernel/simd.hh>

#if defined(building_meta)
#    define MOTOR_API_META MOTOR_EXPORT
#elif defined(motor_dll_meta)
#    define MOTOR_API_META MOTOR_IMPORT
#else
#    define MOTOR_API_META
#endif

#define published public
#define motor_tag(v)

#ifndef MOTOR_COMPUTE
namespace Motor {
namespace Arena {
motor_api(META) minitl::allocator& meta();
motor_api(META) minitl::allocator& script();

}  // namespace Arena

namespace Meta {

struct Class;
struct Type;
class Value;

}  // namespace Meta

namespace Log {

motor_api(META) weak< Logger > meta();

}

}  // namespace Motor

#endif
