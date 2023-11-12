/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <ioprocess.hh>

namespace Motor {

static minitl::allocator& ticketPool()
{
    return Arena::filesystem();  // TODO
}

File::Ticket::Ticket(minitl::allocator& arena, i64 offset, u32 size, bool text, const void* data)
    : action(data == nullptr ? Read : Write)
    , buffer(arena, data != nullptr ? size : 0)
    , processed(i_u32::create(0))
    , offset(offset)
    , total(size)
    , error(i_bool::create(false))
    , text(text)
{
    if(data)
    {
        memcpy(buffer.data(), data, size);
    }
}

File::Ticket::~Ticket() = default;

File::File(const ifilename& filename, u64 size, u64 fileState)
    : m_filename(filename)
    , m_size(size)
    , m_state(fileState)
{
}

File::~File() = default;

ref< const File::Ticket > File::beginRead(u32 size, i64 offset, bool text,
                                          minitl::allocator& arena) const
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
    ref< Ticket > t = doBeginOperation(ticketPool(), arena, nullptr, s, offset, text);
    IOProcess::IOContext::pushTicket(t);
    return t;
}

ref< const File::Ticket > File::beginWrite(const void* data, u32 size, i64 offset) const
{
    if(offset > 0)
        motor_assert((u64)offset <= m_size, "writing past end of file");
    else if(offset < 0)
        motor_assert(offset + (i64)m_size + 1 >= 0, "writing past end of file");
    ref< Ticket > t = doBeginOperation(ticketPool(), Arena::temporary(), data, size, offset, false);
    IOProcess::IOContext::pushTicket(t);
    return t;
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
