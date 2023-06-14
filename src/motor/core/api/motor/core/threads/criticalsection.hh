/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_THREADS_CRITICALSECTION_HH
#define MOTOR_CORE_THREADS_CRITICALSECTION_HH

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
private:
    const CriticalSection& m_section;

public:
    inline explicit ScopedCriticalSection(const CriticalSection& s) : m_section(s)
    {
        this->m_section.enter();
    }
    inline ~ScopedCriticalSection()
    {
        this->m_section.leave();
    }
    ScopedCriticalSection(const ScopedCriticalSection&)            = delete;
    ScopedCriticalSection& operator=(const ScopedCriticalSection&) = delete;
    ScopedCriticalSection(ScopedCriticalSection&&)                 = delete;
    ScopedCriticalSection& operator=(ScopedCriticalSection&&)      = delete;
};

}  // namespace Motor

#endif
