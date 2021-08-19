/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_FILESYSTEM_IOPROCESS_HH_
#define MOTOR_FILESYSTEM_IOPROCESS_HH_
/**************************************************************************************************/
#include <motor/filesystem/stdafx.h>
#include <motor/core/threads/semaphore.hh>
#include <motor/core/threads/thread.hh>
#include <motor/filesystem/file.script.hh>

namespace Motor { namespace IOProcess {

class IOContext : public minitl::pointer
{
private:
    enum
    {
        SlotCount = 32
    };
    Semaphore           m_availableTickets;
    Semaphore           m_freeSlots;
    i_u32               m_firstFreeSlot;
    i_u32               m_firstUsedSlot;
    i_u8                m_ioDone;
    ref< File::Ticket > m_ticketPool[SlotCount];
    Thread              m_ioThread;

private:
    static intptr_t ioProcess(intptr_t p1, intptr_t p2);

public:
    IOContext();
    ~IOContext();

    static void pushTicket(ref< File::Ticket > ticket);
    static void begin();
    static void end();
};

}}  // namespace Motor::IOProcess

/**************************************************************************************************/
#endif
