/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/string/text.hh>

#include <cstring>

namespace Motor {

text::text(const char* str)
    : m_text(str ? Arena::general().strdup(str) : nullptr)
    , m_length(str ? motor_checked_numcast< u32 >(strlen(str)) : 0)
{
}

text::text(const char* begin, const char* end)
    : m_text(Arena::general().strdup(begin, end))
    , m_length(motor_checked_numcast< u32 >(end - begin))
{
}

text::text(const text& other)
    : m_text(other.m_text ? Arena::general().strdup(other.begin(), other.end()) : nullptr)
    , m_length(other.m_length)
{
}

text::~text()
{
    Arena::general().free(m_text);
}

const char* text::begin() const
{
    return m_text;
}

const char* text::end() const
{
    return m_text + m_length;
}

u32 text::length() const
{
    return m_length;
}

u32 text::size() const
{
    return m_length;
}

}  // namespace Motor
