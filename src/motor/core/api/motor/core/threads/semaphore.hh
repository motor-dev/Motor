/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_THREADS_SEMAPHORE_HH_
#define MOTOR_CORE_THREADS_SEMAPHORE_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/core/threads/waitable.hh>

namespace Motor {

class motor_api(CORE) Semaphore : public Threads::Waitable
{
private:
    union Data
    {
        int   value;
        void* ptr;
    };
    Data m_data;

public:
    Semaphore(int initialCount);
    ~Semaphore();

    void                         release(int count);
    virtual Waitable::WaitResult wait() override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
