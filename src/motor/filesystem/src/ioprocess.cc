/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <ioprocess.hh>

namespace Motor { namespace IOProcess {

scoped< IOContext > s_context;
static i_u32        s_contextUseCount;

IOContext::IOContext()
    : m_availableTickets(0)
    , m_freeSlots(MaxRequestCount)
    , m_ioDone(i_u8::create(0))
    , m_ioThread("IOThread", &IOContext::ioProcess, reinterpret_cast< intptr_t >(this), 0,
                 Thread::Highest)
    , m_freeRequestList()
    , m_requestQueue()
{
    for(u32 i = 0; i < MaxRequestCount - 1; ++i)
        m_requests[i].next = &m_requests[i + 1];
    m_requests[MaxRequestCount - 1].next = nullptr;
    m_freeRequestList.pushList(&m_requests[0], &m_requests[MaxRequestCount - 1]);
}

IOContext::~IOContext()
{
    m_ioDone++;
    m_availableTickets.release(1);
    m_ioThread.wait();
}

void IOContext::processRequests(IORequest* head)
{
    if(head->next)
    {
        m_availableTickets.wait();
        processRequests(head->next);
    }

    ref< File::Ticket > ticket = head->ticket;
    head->ticket               = ref< File::Ticket >();
    m_freeRequestList.push(head);
    m_freeSlots.release(1);

    switch(ticket->action)
    {
    case File::Ticket::Read:
        if(!m_ioDone)
        {
            if(ticket->text)
            {
                ticket->buffer.realloc(ticket->total + 1);
                ticket->buffer[ticket->total] = 0;
            }
            else
            {
                ticket->buffer.realloc(ticket->total);
            }
            ticket->processed.set(0);
            ticket->file->fillBuffer(ticket);
        }
        break;
    case File::Ticket::Write: ticket->file->writeBuffer(ticket); break;
    default: motor_error_format(Log::fs(), "unknown IO request: {0}", int(ticket->action)); break;
    }
}

intptr_t IOContext::ioProcess(intptr_t p1, intptr_t /*p2*/)
{
    auto* context = reinterpret_cast< IOContext* >(p1);
    while(true)
    {
        context->m_availableTickets.wait();
        IORequest* requests = context->m_requestQueue.popAll();

        if(!requests)
        {
            motor_assert(context->m_ioDone, "IO context exited but was not yet finished");
            break;
        }
        context->processRequests(requests);
    }
    return 0;
}

void IOContext::pushTicket(const ref< File::Ticket >& ticket)
{
    s_context->m_freeSlots.wait();
    IORequest* request = s_context->m_freeRequestList.pop();
    request->ticket    = ticket;

    s_context->m_requestQueue.push(request);
    s_context->m_availableTickets.release(1);
}

void IOContext::begin()
{
    if(++s_contextUseCount == 1)
    {
        s_context.reset(scoped< IOContext >::create(Arena::filesystem()));
    }
}

void IOContext::end()
{
    if(--s_contextUseCount == 0)
    {
        s_context.reset(scoped< IOContext >());
    }
}

}}  // namespace Motor::IOProcess
