/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_STRING_TEXT_HH
#define MOTOR_CORE_STRING_TEXT_HH

#include <motor/core/coredefs.hh>
#include <motor/minitl/format.hh>

namespace Motor {

struct motor_api(CORE) text
{
private:
    const char* m_text;
    const u32   m_length;

public:
    explicit text(const char* str);
    text(const char* begin, const char* end);
    text(const text& other);
    ~text();

    const char* begin() const;
    const char* end() const;

    u32 length() const;
    u32 size() const;

    explicit operator const char*() const
    {
        return begin();
    }

    text& operator=(const text& other) = delete;
};

static inline u32 format_length(const text& s, const minitl::format_options& options)
{
    motor_forceuse(options);
    return s.size();
}

}  // namespace Motor

#endif
