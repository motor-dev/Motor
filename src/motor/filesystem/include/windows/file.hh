/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_WINDOWS_FILE_HH
#define MOTOR_FILESYSTEM_WINDOWS_FILE_HH

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>

namespace Motor {

class Win32File : public File
{
public:
    Win32File(const ifilename& file, u64 size, u64 timestamp);
    ~Win32File() override;

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
