/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_FILESYSTEM_POSIX_FILE_HH_
#define MOTOR_FILESYSTEM_POSIX_FILE_HH_
/**************************************************************************************************/
#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>

#include <sys/types.h>

namespace Motor {

class PosixFile : public File
{
public:
    PosixFile(ifilename file, File::Media media, u64 size, time_t modifiedTime);
    ~PosixFile();

    void refresh(u64 size, time_t modifiedTime);

private:
    virtual void doFillBuffer(weak< File::Ticket > ticket) const override;
    virtual void doWriteBuffer(weak< Ticket > ticket) const override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
