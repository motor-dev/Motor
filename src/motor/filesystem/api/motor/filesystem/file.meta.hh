/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_FILE_META_HH
#define MOTOR_FILESYSTEM_FILE_META_HH

#include <motor/filesystem/stdafx.h>
#include <motor/core/string/istring.hh>
#include <motor/kernel/interlocked_stack.hh>
#include <motor/minitl/intrusive_list.hh>

namespace Motor {

namespace IOProcess {
class IOContext;
}

class Folder;

class motor_api(FILESYSTEM) File : public minitl::pointer
{
    friend class Folder;

public:
    class [[motor::meta(export = no)]] Ticket;
    friend class Ticket;

protected:
    const ifilename m_filename;
    u64             m_size;
    u64             m_state;

protected:
    File(ifilename filename, u64 size, u64 state);

    virtual ref< Ticket > doBeginOperation(minitl::allocator & ticketArena,
                                           minitl::allocator & dataArena, const void* data,
                                           u32 size, i64 offset, bool text) const
        = 0;

public:
    ~File() override;

public:
    class [[motor::meta(export = no)]] Ticket : public minitl::pointer
    {
        friend class IOProcess::IOContext;

    public:
        enum Action
        {
            Read,
            Write
        };
        Action const                   action;
        minitl::allocator::block< u8 > buffer;
        i_u32                          processed;
        const i64                      offset;
        const u32                      total;
        i_bool                         error;
        bool                           text;

        inline bool done() const
        {
            return error || processed == total;
        }

    public:
        Ticket(minitl::allocator& arena, i64 offset, u32 size, bool text, const void* data);
        ~Ticket() override;

    private:  // friend class IOProcess;
        virtual void fillBuffer()  = 0;
        virtual void writeBuffer() = 0;
    };

    [[motor::meta(export = no)]] ref< const Ticket > beginRead(
        u32 size = 0, i64 offset = 0, bool text = false,
        minitl::allocator& arena = Arena::temporary()) const;
    [[motor::meta(export = no)]] ref< const Ticket > beginWrite(const void* data, u32 size,
                                                                i64 offset = -1) const;

    [[motor::meta(export = no)]] u64  getState() const;
    [[motor::meta(export = no)]] bool isDeleted() const;
    [[motor::meta(export = no)]] void refresh(u64 fileSize, u64 state);

    ifilename getFileName() const
    {
        return m_filename;
    }
};

}  // namespace Motor

#endif
