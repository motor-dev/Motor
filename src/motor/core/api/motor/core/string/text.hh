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

    operator const char*() const
    {
        return begin();
    }

private:
    text& operator=(const text& other);
    text();
};

}  // namespace Motor

namespace minitl {

template <>
struct formatter< Motor::text > : public formatter< const char* >
{
    static u32 length(const Motor::text& value, const format_options& options)
    {
        motor_forceuse(options);
        return value.length();
    }
};

}  // namespace minitl

/**************************************************************************************************/
#endif
