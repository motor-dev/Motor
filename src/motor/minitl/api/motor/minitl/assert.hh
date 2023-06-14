/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_ASSERT_HH
#define MOTOR_MINITL_ASSERT_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <stdlib.h>

namespace minitl {

enum struct assertion_result
{
    abort,
    ignore,
    ignore_all,
    breakpoint
};

typedef assertion_result (*assertion_callback_t)(const char* filename, int line, const char* expr,
                                                 const char* message);

motor_api(MINITL) assertion_callback_t set_assertion_callback(assertion_callback_t callback);
motor_api(MINITL) assertion_callback_t get_assertion_callback();

#if !(MOTOR_ENABLE_ASSERT)
static inline bool assertCondition()
{
    return false;
}
// NOLINTNEXTLINE(readability-identifier-naming)
#    define motor_assert_impl_(cond, msg) ::minitl::assertCondition()
#else
// NOLINTNEXTLINE(readability-identifier-naming)
#    define motor_assert_impl_(cond, msg)                                                          \
        (!(cond) && [&]() {                                                                        \
            static bool s_ignoreAll = false;                                                       \
            if(!s_ignoreAll)                                                                       \
            {                                                                                      \
                minitl::assertion_result motor_r_;                                                 \
                motor_r_ = minitl::get_assertion_callback()(MOTOR_FILE, MOTOR_LINE, #cond, msg);   \
                switch(motor_r_)                                                                   \
                {                                                                                  \
                case minitl::assertion_result::abort: ::abort(); break;                            \
                case minitl::assertion_result::ignore: break;                                      \
                case minitl::assertion_result::ignore_all: s_ignoreAll = true; break;              \
                case minitl::assertion_result::breakpoint: motor_break(); break;                   \
                default:;                                                                          \
                }                                                                                  \
            }                                                                                      \
            return true;                                                                           \
        }())
#endif

// NOLINTNEXTLINE(readability-identifier-naming)
#define motor_assert(cond, msg) motor_assert_impl_(cond, msg)
// NOLINTNEXTLINE(readability-identifier-naming)
#define motor_assert_format(cond, msg, ...)                                                        \
    motor_assert_impl_(cond, minitl::format< 4096 >(FMT(msg), __VA_ARGS__))
// NOLINTNEXTLINE(readability-identifier-naming)
#define motor_unimplemented() motor_assert_impl_(!"implemented", "not implemented")
// NOLINTNEXTLINE(readability-identifier-naming)
#define motor_notreached() motor_assert_impl_(!"reached", "should not reach code")

}  // namespace minitl

#endif
