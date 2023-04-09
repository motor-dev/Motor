/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_ASSERT_HH_
#define MOTOR_MINITL_ASSERT_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <cstdlib>

namespace minitl {

enum struct AssertionResult
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
static inline bool assertCondition()
{
    return false;
}
#    define motor_assert_impl_(cond, msg) ::minitl::assertCondition()
#else
#    define motor_assert_impl_(cond, msg)                                                          \
        (!(cond) && [&]() {                                                                        \
            static bool ignoreAll = false;                                                         \
            if(!ignoreAll)                                                                         \
            {                                                                                      \
                minitl::AssertionResult motor_r_;                                                  \
                motor_r_ = minitl::getAssertionCallback()(__FILE__, __LINE__, #cond, msg);         \
                switch(motor_r_)                                                                   \
                {                                                                                  \
                case minitl::AssertionResult::Abort: ::abort(); break;                             \
                case minitl::AssertionResult::Ignore: break;                                       \
                case minitl::AssertionResult::IgnoreAll: ignoreAll = true; break;                  \
                case minitl::AssertionResult::Break: motor_break(); break;                         \
                default:;                                                                          \
                }                                                                                  \
            }                                                                                      \
            return true;                                                                           \
        }())
#endif

#define motor_assert(cond, msg) motor_assert_impl_(cond, msg)
#define motor_assert_format(cond, msg, ...)                                                        \
    motor_assert_impl_(cond, minitl::format< 4096 >(FMT(msg), __VA_ARGS__))
#define motor_unimplemented() motor_assert_impl_(!"implemented", "not implemented")
#define motor_notreached()    motor_assert_impl_(!"reached", "should not reach code")

}  // namespace minitl

/**************************************************************************************************/
#endif
