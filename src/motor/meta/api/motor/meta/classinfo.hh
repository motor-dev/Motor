/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_CLASSINFO_HH
#define MOTOR_META_CLASSINFO_HH

#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {
class Class;

template < typename T >
struct ClassID
{
    constexpr static raw< const Class > klass() = delete;
    static istring                      name()  = delete;
};

#define MOTOR_DECLARE_CLASS_ID(module, template_params, type)                                      \
    template < template_params >                                                                   \
    struct ClassID< type >                                                                         \
    {                                                                                              \
        constexpr static raw< const Class > klass()                                                \
        {                                                                                          \
            return {&s_class};                                                                     \
        }                                                                                          \
        motor_api(module) static istring name();                                                   \
        motor_api(module) static const Class s_class;                                              \
    };                                                                                             \
    extern template struct ClassID< type >;

MOTOR_DECLARE_CLASS_ID(META, /*none*/, void)
MOTOR_DECLARE_CLASS_ID(META, /*none*/, minitl::pointer)
}}  // namespace Motor::Meta

#endif
