/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_POSIX_FILE_HH
#define MOTOR_FILESYSTEM_POSIX_FILE_HH

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>

#include <sys/types.h>

namespace Motor {

class PosixFile : public File
{
public:
    PosixFile(const ifilename& file, u64 size, time_t modifiedTime);
    ~PosixFile() override;

    void refresh(u64 size, time_t modifiedTime);

private:
    ref< Ticket > doBeginOperation(minitl::allocator& ticketArena, minitl::allocator& dataArena,
                                   const void* data, u32 size, i64 offset,
                                   bool text) const override;

private:
    class Ticket : public File::Ticket
    {
    private:
        ifilename m_filename;

    public:
        Ticket(ifilename filename, minitl::allocator& arena, i64 offset, u32 size, bool text,
               const void* data);

    private:
        void fillBuffer() override;
        void writeBuffer() override;
    };
};

}  // namespace Motor

#endif
