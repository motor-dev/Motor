/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_ZIPFILE_HH
#define MOTOR_FILESYSTEM_ZIPFILE_HH

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>

#include <stdio.h>
#include <stdlib.h>

#include <unzip.h>

namespace Motor {

class ZipFile : public File
{
private:
    unzFile      m_handle;
    unz_file_pos m_filePos;

public:
    ZipFile(void* handle, const ifilename& filename, const unz_file_info& fileInfo,
            const unz_file_pos& filePos);
    ~ZipFile() override;

private:
    void doFillBuffer(const weak< File::Ticket >& ticket) const override;
    void doWriteBuffer(const weak< Ticket >& ticket) const override;
};

}  // namespace Motor

#endif
