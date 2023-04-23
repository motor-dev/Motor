/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    void doFillBuffer(const weak< File::Ticket >& ticket) const override;
    void doWriteBuffer(const weak< Ticket >& ticket) const override;
};

}  // namespace Motor
