/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_THREADS_CRITICALSECTION_HH_
#define MOTOR_CORE_THREADS_CRITICALSECTION_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>

namespace Motor {

class ScopedCriticalSection;

class motor_api(CORE) CriticalSection
{
    friend class ScopedCriticalSection;

private:
    void* m_data;

public:
    CriticalSection();
    ~CriticalSection();

private:
    void enter() const;
    void leave() const;
};

class ScopedCriticalSection
{
    MOTOR_NOCOPY(ScopedCriticalSection);

private:
    const CriticalSection& m_section;

public:
    inline ScopedCriticalSection(const CriticalSection& s) : m_section(s)
    {
        m_section.enter();
    }
    inline ~ScopedCriticalSection()
    {
        m_section.leave();
    }
};

}  // namespace Motor

/**************************************************************************************************/
#endif
