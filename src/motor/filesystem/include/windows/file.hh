/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_FILESYSTEM_WIN32_FILE_HH_
#define MOTOR_FILESYSTEM_WIN32_FILE_HH_
/**************************************************************************************************/
#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.script.hh>

namespace Motor {

class Win32File : public File
{
public:
    Win32File(ifilename file, File::Media media, u64 size, u64 timestamp);
    ~Win32File();

    void refresh(u64 size, u64 timestamp);

private:
    void         doFillBuffer(weak< File::Ticket > ticket) const override;
    virtual void doWriteBuffer(weak< Ticket > ticket) const override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
