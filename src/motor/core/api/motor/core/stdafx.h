/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>
#include <motor/kernel/simd.hh>

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
motor_api(CORE) minitl::Allocator& temporary();
motor_api(CORE) minitl::Allocator& stack();
motor_api(CORE) minitl::Allocator& debug();
motor_api(CORE) minitl::Allocator& general();
}}  // namespace Motor::Arena

#    include <motor/minitl/assert.hh>

#    include <motor/minitl/cast.hh>
#    include <motor/minitl/rawptr.hh>
#    include <motor/minitl/refcountable.hh>
#    include <motor/minitl/refptr.hh>
#    include <motor/minitl/scopedptr.hh>
#    include <motor/minitl/weakptr.hh>

#    include <motor/core/string/istring.hh>
#    include <motor/core/string/text.hh>

#    include <motor/core/logger.hh>

using minitl::motor_checked_cast;
using minitl::motor_checked_numcast;
using minitl::motor_function_cast;
using minitl::raw;
using minitl::ref;
using minitl::scoped;
using minitl::weak;

namespace Motor { namespace Log {

motor_api(CORE) weak< Logger > motor();
motor_api(CORE) weak< Logger > system();
motor_api(CORE) weak< Logger > thread();

}}  // namespace Motor::Log

#endif
