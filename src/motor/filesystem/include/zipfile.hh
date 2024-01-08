/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_ZIPFILE_HH
#define MOTOR_FILESYSTEM_ZIPFILE_HH

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/filesystem/zipfolder.meta.hh>

#include <stdio.h>
#include <stdlib.h>

#include <unzip.h>

namespace Motor {

class ZipFile : public File
{
private:
    ref< ZipFolder::Handle > m_handle;
    unz_file_pos             m_filePos;

public:
    ZipFile(const ref< ZipFolder::Handle >& handle, const ifilename& filename,
            const unz_file_info& fileInfo, const unz_file_pos& filePos);
    ~ZipFile() override;

private:
    ref< Ticket > doBeginOperation(minitl::allocator& ticketArena, minitl::allocator& dataArena,
                                   const void* data, u32 size, i64 offset,
                                   bool text) const override;

private:
    class Ticket : public File::Ticket
    {
    private:
        ifilename                m_filename;
        ref< ZipFolder::Handle > m_handle;
        unz_file_pos             m_filePos;

    public:
        Ticket(ifilename filename, const ref< ZipFolder::Handle >& handle,
               const unz_file_pos& filePos, minitl::allocator& arena, i64 offset, u32 size,
               bool text, const void* data);

    private:
        void fillBuffer() override;
        void writeBuffer() override;
    };
};

}  // namespace Motor

#endif
