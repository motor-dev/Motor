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
    constexpr static raw< const Class > klass()
    {
        return {&s_class};
    }
    MOTOR_EXPORT static istring     name();
    MOTOR_EXPORT static const Class s_class;
};

#define MOTOR_DECLARE_CLASS_ID(type)                                                               \
    template <>                                                                                    \
    istring ClassID< type >::name();                                                               \
    template <>                                                                                    \
    const Class                 ClassID< type >::s_class;                                          \
    extern template istring     ClassID< type >::name();                                           \
    extern template const Class ClassID< type >::s_class;

MOTOR_DECLARE_CLASS_ID(void)
MOTOR_DECLARE_CLASS_ID(minitl::pointer)

}}  // namespace Motor::Meta

#endif
