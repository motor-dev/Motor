/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_THREADS_EVENT_HH_
#define MOTOR_CORE_THREADS_EVENT_HH_
/**************************************************************************************************/
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
    ~Event();

    void                         set();
    void                         pulse();
    void                         lock();
    void                         unlock();
    virtual Waitable::WaitResult wait() override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
