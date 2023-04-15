/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <ioprocess.hh>

namespace Motor {

static minitl::Allocator& ticketPool()
{
    return Arena::filesystem();  // TODO
}

File::Ticket::Ticket(minitl::Allocator& arena, const weak< const File >& file, i64 offset, u32 size,
                     bool text)
    : action(Read)
    , file(file)
    , buffer(arena, 0)
    , processed(i_u32::create(0))
    , offset(offset)
    , total(size)
    , error(i_bool::create(false))
    , text(text)
{
    file->addref();
}

File::Ticket::Ticket(minitl::Allocator& arena, const weak< const File >& file, i64 offset, u32 size,
                     bool text, const void* data)
    : action(Write)
    , file(file)
    , buffer(arena, size)
    , processed(i_u32::create(0))
    , offset(offset)
    , total(size)
    , error(i_bool::create(false))
    , text(text)
{
    memcpy(buffer.data(), data, size);
    file->addref();
}

File::Ticket::~Ticket()
{
    const File* f = file.operator->();
    file          = weak< const File >();
    f->decref();
}

File::File(const ifilename& filename, u64 size, u64 fileState)
    : m_filename(filename)
    , m_size(size)
    , m_state(fileState)
{
}

File::~File() = default;

ref< const File::Ticket > File::beginRead(u32 size, i64 offset, bool text,
                                          minitl::Allocator& arena) const
{
    u32 s;
    if(offset >= 0)
    {
        motor_assert((u64)offset <= m_size, "reading past end of file");
        motor_assert((u64)offset + size <= m_size, "reading past end of file");
        s = size ? size : motor_checked_numcast< u32 >(m_size - offset);
    }
    else
    {
        motor_assert(offset + (i64)m_size + 1 >= 0, "reading past end of file");
        motor_assert(m_size + offset + size + 1 <= m_size, "reading past end of file");
        s = size ? size : motor_checked_numcast< u32 >((i64)m_size + offset + (text ? 1 : 0));
    }
    ref< Ticket > t = ref< Ticket >::create(ticketPool(), byref(arena), this, offset, s, text);
    IOProcess::IOContext::pushTicket(t);
    return t;
}

ref< const File::Ticket > File::beginWrite(const void* data, u32 size, i64 offset)
{
    if(offset > 0)
        motor_assert((u64)offset <= m_size, "writing past end of file");
    else if(offset < 0)
        motor_assert(offset + (i64)m_size + 1 >= 0, "writing past end of file");
    ref< Ticket > t = ref< Ticket >::create(ticketPool(), byref(Arena::temporary()), this, offset,
                                            size, false, data);
    IOProcess::IOContext::pushTicket(t);
    return t;
}

void File::fillBuffer(const weak< Ticket >& ticket) const
{
    motor_assert(ticket->file == this, "trying to fill buffer of another file");
    doFillBuffer(ticket);
}

void File::writeBuffer(const weak< Ticket >& ticket) const
{
    motor_assert(ticket->file == this, "trying to fill buffer of another file");
    doWriteBuffer(ticket);
}

u64 File::getState() const
{
    return m_state;
}

bool File::isDeleted() const
{
    return m_state == ~(u64)0;
}

void File::refresh(u64 fileSize, u64 fileState)
{
    if(fileSize != m_size || fileState != m_state)
    {
        m_size = fileSize;
        if(fileState != m_state)
        {
            m_state = fileState;
        }
        else
        {
            m_state++;
        }
    }
}

}  // namespace Motor
