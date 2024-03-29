/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_STDAFX_H
#define MOTOR_META_STDAFX_H

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

#define motor_meta(x)

#ifndef MOTOR_COMPUTE
namespace Motor {
namespace Arena {
motor_api(META) minitl::allocator& meta();
motor_api(META) minitl::allocator& script();

}  // namespace Arena

namespace Meta {

class Class;
struct Type;
class Value;

}  // namespace Meta

namespace Log {

motor_api(META) weak< Logger > meta();

}

}  // namespace Motor

#endif

#endif
