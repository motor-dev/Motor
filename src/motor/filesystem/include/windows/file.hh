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
    void doFillBuffer(const weak< File::Ticket >& ticket) const override;
    void doWriteBuffer(const weak< Ticket >& ticket) const override;
};

}  // namespace Motor

#endif
