/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>

namespace Motor {

class Win32File : public File
{
public:
    Win32File(ifilename file, u64 size, u64 timestamp);
    ~Win32File() override;

private:
    void doFillBuffer(weak< File::Ticket > ticket) const override;
    void doWriteBuffer(weak< Ticket > ticket) const override;
};

}  // namespace Motor
