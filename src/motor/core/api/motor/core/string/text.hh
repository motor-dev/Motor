/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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

static inline u32 format_length(const text& s, const minitl::format_options& options)
{
    motor_forceuse(options);
    return s.size();
}

}  // namespace Motor
