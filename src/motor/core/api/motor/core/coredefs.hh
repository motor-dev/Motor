/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_COREDEFS_HH
#define MOTOR_CORE_COREDEFS_HH

#include <motor/kernel/stdafx.h>

#ifndef MOTOR_COMPUTE
#    include <motor/minitl/stdafx.h>

#    include <motor/core/preproc.hh>
#    ifdef _MSC_VER
#        define MOTOR_FUNCTION __FUNCSIG__
#    elif defined(__GNUC__)
#        define MOTOR_FUNCTION __PRETTY_FUNCTION__
#    else
#        define MOTOR_FUNCTION __FUNCTION__
#    endif
#    define MOTOR_PROJECT                                                                          \
        MOTOR_STRINGIZE(MOTOR_PROJECTCATEGORY) "." MOTOR_STRINGIZE(MOTOR_PROJECTNAME)
#    define MOTOR_HERE MOTOR_FILE ":" MOTOR_LINE "\n\t[ " MOTOR_FUNCTION " ]\t"

#    if defined(building_core)
#        define MOTOR_API_CORE MOTOR_EXPORT
#    elif defined(motor_dll_core)
#        define MOTOR_API_CORE MOTOR_IMPORT
#    else
#        define MOTOR_API_CORE
#    endif

#    include <motor/minitl/allocator.hh>

namespace Motor { namespace Arena {
motor_api(CORE) minitl::allocator& temporary();
motor_api(CORE) minitl::allocator& stack();
motor_api(CORE) minitl::allocator& debug();
motor_api(CORE) minitl::allocator& general();
}}  // namespace Motor::Arena

#    include <motor/minitl/assert.hh>

#    include <motor/minitl/cast.hh>
#    include <motor/minitl/rawptr.hh>
#    include <motor/minitl/refcountable.hh>
#    include <motor/minitl/refptr.hh>
#    include <motor/minitl/scopedptr.hh>
#    include <motor/minitl/weakptr.hh>

using minitl::motor_checked_cast;
using minitl::motor_checked_numcast;
using minitl::motor_function_cast;
using minitl::raw;
using minitl::ref;
using minitl::scoped;
using minitl::weak;

#endif

#endif