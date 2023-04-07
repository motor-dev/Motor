/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <zipfile.hh>

namespace Motor {

ZipFile::ZipFile(void* handle, const ifilename& filename, const unz_file_info& info,
                 const unz_file_pos& filePos)
    : File(filename, File::Media(File::Media::Package, 0, 0), u64(info.uncompressed_size),
           u64(info.dosDate))
    , m_handle(handle)
    , m_filePos(filePos)
{
    motor_info_format(Log::fs(), "created zip file {0}", m_filename);
}

ZipFile::~ZipFile()
{
}

void ZipFile::doFillBuffer(weak< File::Ticket > ticket) const
{
    /* state of the previous read */
    static const unz_file_pos* s_currentFile = 0;
    static i64                 s_fileOffset  = 0;
    unz_file_pos               filePos       = m_filePos;

    motor_assert(ticket->file == this, "trying to read wrong file");
    if(s_currentFile != &m_filePos || s_fileOffset > ticket->offset)
    {
        s_currentFile = &m_filePos;
        s_fileOffset  = 0;
        unzCloseCurrentFile(m_handle);
        int result = unzGoToFilePos(m_handle, &filePos);
        motor_assert_format(result == UNZ_OK, "could not go to file {0}", m_filename);
        result = unzOpenCurrentFile(m_handle);
        motor_assert_format(result == UNZ_OK, "could not open file {0}", m_filename);
        motor_forceuse(result);
    }

    while(s_fileOffset < ticket->offset)
    {
        u8  buffer[4096];
        i64 bytesToRead = minitl::min< i64 >(4096, ticket->offset - s_fileOffset);
        i64 read        = unzReadCurrentFile(m_handle, buffer,
                                             motor_checked_numcast< unsigned int >(bytesToRead));
        s_fileOffset += read;
    }

    motor_assert_format(ticket->buffer.byteCount() > ticket->total,
                        "buffer is not long enough to read entire file; "
                        "buffer size is {0}, requires {1} bytes",
                        ticket->buffer.byteCount(), ticket->total);
    u8* buffer = ticket->buffer.begin();
    while(!ticket->done())
    {
        i64 bytesToRead = ticket->total - ticket->processed;
        u32 bytesRead
            = unzReadCurrentFile(m_handle, buffer, motor_checked_numcast< u32 >(bytesToRead));
        if(bytesRead > 0)
        {
            ticket->processed += bytesRead;
            buffer += bytesRead;
        }
        else
        {
            motor_error_format(Log::fs(), "error {0} while reading from file {1}", bytesRead,
                               m_filename);
        }
    }

    s_fileOffset  = 0;
    s_currentFile = 0;
}

void ZipFile::doWriteBuffer(weak< Ticket > ticket) const
{
    motor_forceuse(ticket);
    motor_notreached();
}

}  // namespace Motor
