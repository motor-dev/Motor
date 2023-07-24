/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_THREADS_EVENT_HH
#define MOTOR_CORE_THREADS_EVENT_HH

#include <motor/core/stdafx.h>
#include <motor/core/threads/waitable.hh>

namespace Motor {

class motor_api(CORE) Event : public Threads::Waitable
{
private:
    void* m_data;
    void* m_lock;

public:
    Event();
    ~Event() noexcept override;

    void                 set();
    void                 pulse();
    void                 lock();
    void                 unlock();
    Waitable::WaitResult wait() override;
};

}  // namespace Motor

#endif
