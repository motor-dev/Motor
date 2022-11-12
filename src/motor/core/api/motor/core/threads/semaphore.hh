/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/core/threads/waitable.hh>

namespace Motor {

class motor_api(CORE) Semaphore : public Threads::Waitable
{
private:
    union Data
    {
        i_u32 value;
        void* ptr;
    };
    Data m_data;

public:
    Semaphore(int initialCount);
    ~Semaphore();

    void                         release(int count);
    virtual Waitable::WaitResult wait() override;

    static u32 flushPauseCount();
};

}  // namespace Motor
