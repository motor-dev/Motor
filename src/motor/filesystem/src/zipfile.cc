/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <zipfile.hh>

namespace Motor {

ZipFile::ZipFile(const ref< ZipFolder::Handle >& handle, const ifilename& filename,
                 const unz_file_info& info, const unz_file_pos& filePos)
    : File(filename, u64(info.uncompressed_size), u64(info.dosDate))
    , m_handle(handle)
    , m_filePos(filePos)
{
    motor_info_format(Log::fs(), "created zip file {0}", m_filename);
}

ZipFile::~ZipFile() = default;

ref< File::Ticket > ZipFile::doBeginOperation(minitl::allocator& ticketArena,
                                              minitl::allocator& dataArena, const void* data,
                                              u32 size, i64 offset, bool text) const
{
    return ref< Ticket >::create(ticketArena, m_filename, m_handle, m_filePos, dataArena, offset,
                                 size, text, data);
}

ZipFile::Ticket::Ticket(ifilename filename, const ref< ZipFolder::Handle >& handle,
                        const unz_file_pos& filePos, minitl::allocator& arena, i64 offset, u32 size,
                        bool text, const void* data)
    : File::Ticket(arena, offset, size, text, data)
    , m_filename(minitl::move(filename))
    , m_handle(handle)
    , m_filePos(filePos)
{
}

void ZipFile::Ticket::fillBuffer()
{
    /* state of the previous read */
    static const unz_file_pos* s_currentFile = nullptr;
    static i64                 s_fileOffset  = 0;
    unz_file_pos               filePos       = m_filePos;

    if(s_currentFile != &m_filePos || s_fileOffset > offset)
    {
        s_currentFile = &m_filePos;
        s_fileOffset  = 0;
        unzCloseCurrentFile(*m_handle);
        int result = unzGoToFilePos(*m_handle, &filePos);
        motor_assert_format(result == UNZ_OK, "could not go to file {0}", m_filename);
        result = unzOpenCurrentFile(*m_handle);
        motor_assert_format(result == UNZ_OK, "could not open file {0}", m_filename);
        motor_forceuse(result);
    }

    while(s_fileOffset < offset)
    {
        u8  discard[4096];
        i64 bytesToRead = minitl::min< i64 >(4096, offset - s_fileOffset);
        i64 read        = unzReadCurrentFile(*m_handle, discard,
                                             motor_checked_numcast< unsigned int >(bytesToRead));
        s_fileOffset += read;
    }

    motor_assert_format(buffer.byte_count() > total,
                        "buffer is not long enough to read entire file; "
                        "buffer size is {0}, requires {1} bytes",
                        buffer.byte_count(), total);
    u8* targetBuffer = buffer.begin();
    while(!done())
    {
        u32 bytesToRead = motor_checked_numcast< u32 >(total - processed);
        u32 bytesRead   = unzReadCurrentFile(*m_handle, targetBuffer, bytesToRead);
        if(bytesRead > 0)
        {
            processed += bytesRead;
            targetBuffer += bytesRead;
        }
        else
        {
            motor_error_format(Log::fs(), "error {0} while reading from file {1}", bytesRead,
                               m_filename);
        }
    }

    s_fileOffset  = 0;
    s_currentFile = nullptr;
}

void ZipFile::Ticket::writeBuffer()
{
    motor_notreached();
}

}  // namespace Motor
