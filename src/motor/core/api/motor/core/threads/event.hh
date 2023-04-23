/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    ~Event() override;

    void                 set();
    void                 pulse();
    void                 lock();
    void                 unlock();
    Waitable::WaitResult wait() override;
};

}  // namespace Motor
