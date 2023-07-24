/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_THREADS_SEMAPHORE_HH
#define MOTOR_CORE_THREADS_SEMAPHORE_HH

#include <motor/core/stdafx.h>
#include <motor/core/threads/waitable.hh>

namespace Motor {

class motor_api(CORE) Semaphore : public Threads::Waitable
{
private:
    union Data
    {
        i_i32 value {};
        void* ptr;
    };
    Data m_data;

public:
    explicit Semaphore(int initialCount);
    ~Semaphore() noexcept override;

    void                 release(int count);
    Waitable::WaitResult wait() override;

    static u32 flushPauseCount();
};

}  // namespace Motor

#endif
