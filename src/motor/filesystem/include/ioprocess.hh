/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_FILESYSTEM_IOPROCESS_HH_
#define MOTOR_FILESYSTEM_IOPROCESS_HH_
/**************************************************************************************************/
#include <motor/filesystem/stdafx.h>
#include <motor/core/threads/semaphore.hh>
#include <motor/core/threads/thread.hh>
#include <motor/filesystem/file.meta.hh>
#include <motor/kernel/interlocked_stack.hh>

namespace Motor { namespace IOProcess {

class IOContext : public minitl::pointer
{
private:
    struct IORequest : public kernel::istack< IORequest >::node
    {
        ref< File::Ticket > ticket;
    };
    enum
    {
        MaxRequestCount = 32
    };
    Semaphore m_availableTickets;
    Semaphore m_freeSlots;
    i_u8      m_ioDone;
    Thread    m_ioThread;

    IORequest                   m_requests[MaxRequestCount];
    kernel::istack< IORequest > m_freeRequestList;
    kernel::istack< IORequest > m_requestQueue;

private:
    static intptr_t ioProcess(intptr_t p1, intptr_t p2);
    void            processRequests(IORequest* head);

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
