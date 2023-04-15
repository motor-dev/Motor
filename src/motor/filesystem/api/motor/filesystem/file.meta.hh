/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/filesystem/stdafx.h>
#include <motor/core/string/istring.hh>
#include <motor/kernel/interlocked_stack.hh>
#include <motor/minitl/intrusive_list.hh>

namespace Motor {

class Folder;

class motor_api(FILESYSTEM) File : public minitl::refcountable
{
    friend class Folder;

public:
    class Ticket;
    friend class Ticket;

protected:
    const ifilename m_filename;
    u64             m_size;
    u64             m_state;

protected:
    File(const ifilename& filename, u64 size, u64 state);

public:
    ~File() override;

public:
    class Ticket : public minitl::refcountable
    {
        friend class File;

    public:
        enum Action
        {
            Read,
            Write
        };
        Action const                   action;
        weak< const File >             file;
        minitl::Allocator::Block< u8 > buffer;
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
        Ticket(minitl::Allocator& arena, const weak< const File >& file, i64 offset, u32 size,
               bool text);
        Ticket(minitl::Allocator& arena, const weak< const File >& file, i64 offset, u32 size,
               bool text, const void* data);
        ~Ticket() override;

    private:
        Ticket(const Ticket&);
        Ticket& operator=(const Ticket&);
    };

    ref< const Ticket > beginRead(u32 size = 0, i64 offset = 0, bool text = false,
                                  minitl::Allocator& arena = Arena::temporary()) const;
    ref< const Ticket > beginWrite(const void* data, u32 size, i64 offset = -1);

    void fillBuffer(const weak< Ticket >& ticket) const;
    void writeBuffer(const weak< Ticket >& ticket) const;

    u64  getState() const;
    bool isDeleted() const;
    void refresh(u64 fileSize, u64 state);

    ifilename getFileName() const
    {
        return m_filename;
    }

private:
    virtual void doFillBuffer(weak< Ticket > ticket) const  = 0;
    virtual void doWriteBuffer(weak< Ticket > ticket) const = 0;
};

}  // namespace Motor
