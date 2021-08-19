/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_ASSERT_HH_
#define MOTOR_MINITL_ASSERT_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <cstdlib>
#include <motor/minitl/format.hh>

namespace minitl {

enum AssertionResult
{
    Abort,
    Ignore,
    IgnoreAll,
    Break
};

typedef AssertionResult (*AssertionCallback_t)(const char* filename, int line, const char* expr,
                                               const char* message);
motor_api(MINITL) AssertionCallback_t setAssertionCallback(AssertionCallback_t callback);
motor_api(MINITL) AssertionCallback_t getAssertionCallback();

#if !(MOTOR_ENABLE_ASSERT)
#    define motor_assert_impl_(cond, message, code) ((void)0)
#else
#    ifdef assert
#        undef assert
#    endif
#    define motor_assert_impl_(cond, message, code)                                                \
        do                                                                                         \
        {                                                                                          \
            static bool motor_ignore_ = false;                                                     \
            if(!motor_ignore_ && !(cond))                                                          \
            {                                                                                      \
                minitl::AssertionResult motor_r_;                                                  \
                motor_r_ = minitl::getAssertionCallback()(__FILE__, __LINE__, #cond,               \
                                                          (minitl::format< 4096 >)message);        \
                switch(motor_r_)                                                                   \
                {                                                                                  \
                case minitl::Abort: ::abort(); break;                                              \
                case minitl::IgnoreAll: motor_ignore_ = true; break;                               \
                case minitl::Break: motor_break(); break;                                          \
                default:;                                                                          \
                }                                                                                  \
                code;                                                                              \
            }                                                                                      \
        } while(0)
#endif

#define motor_assert(cond, message)               motor_assert_impl_(cond, message, ;)
#define motor_assert_recover(cond, message, code) motor_assert_impl_(cond, message, code)
#define motor_unimplemented()                     motor_assert_impl_(!"implemented", "not implemented", ;)
#define motor_notreached()                        motor_assert_impl_(!"reached", "should not reach code", ;)

}  // namespace minitl

/**************************************************************************************************/
#endif
