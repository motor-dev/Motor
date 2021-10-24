/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_STRING_TEXT_HH_
#define MOTOR_CORE_STRING_TEXT_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/minitl/format.hh>

namespace Motor {

struct motor_api(CORE) text
{
private:
    const char* m_text;
    const u32   m_length;

public:
    text(const char* str);
    text(const char* begin, const char* end);
    text(const text& other);
    ~text();

    const char* begin() const;
    const char* end() const;

    u32 length() const;
    u32 size() const;

private:
    text& operator=(const text& other);
    text();
};

}  // namespace Motor

namespace minitl {

template < u16 SIZE >
const format< SIZE >& operator|(const format< SIZE >& f, const Motor::text& value)
{
    return f | value.begin();
}

}  // namespace minitl

/**************************************************************************************************/
#endif
