/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <errno.h>
#include <posix/file.hh>
#include <stdio.h>

namespace Motor {

PosixFile::PosixFile(const ifilename& filename, u64 size, time_t modifiedTime)
    : File(filename, size, modifiedTime)
{
}

PosixFile::~PosixFile() = default;

void PosixFile::refresh(u64 size, time_t modifiedTime)
{
    File::refresh(size, modifiedTime);
}

ref< File::Ticket > PosixFile::doBeginOperation(minitl::allocator& ticketArena,
                                                minitl::allocator& dataArena, const void* data,
                                                u32 size, i64 offset, bool text) const
{
    return ref< Ticket >::create(ticketArena, m_filename, dataArena, offset, size, text, data);
}

PosixFile::Ticket::Ticket(const ifilename& filename, minitl::allocator& arena, i64 offset, u32 size,
                          bool text, const void* data)
    : File::Ticket(arena, offset, size, text, data)
    , m_filename(filename)
{
}

void PosixFile::Ticket::fillBuffer()
{
    static const int g_bufferSize = 1024;

    ifilename::Filename pathname = m_filename.str();
    FILE*               f        = fopen(pathname.name, "rb");
    if(!f)
    {
        const char* errorMessage = strerror(errno);
        motor_forceuse(errorMessage);
        motor_error_format(Log::fs(), "file {0} could not be opened: ({1}) {2}", m_filename, errno,
                           errorMessage);
        error.set(true);
    }
    else
    {
        if(offset > 0)
        {
            fseek(f, (long)offset, SEEK_SET);
        }
        else if(offset < 0)
        {
            fseek(f, (long)offset + 1, SEEK_END);
        }
        u8* data = buffer.data();
        for(processed.set(0); !done();)
        {
            size_t read = (processed + g_bufferSize > total)
                              ? fread(data, 1, motor_checked_numcast< u32 >(total - processed), f)
                              : fread(data, 1, g_bufferSize, f);
            processed += (u32)read;
            data += read;
            if(read == 0)
            {
                motor_error_format(
                    Log::fs(),
                    "reached premature end of file in {0} after reading {1} bytes (offset {2})",
                    m_filename, processed, total);
                error.set(true);
            }
        }
        fclose(f);
    }
}

void PosixFile::Ticket::writeBuffer()
{
    static const int g_bufferSize = 1024;

    ifilename::Filename pathname = m_filename.str();
    FILE*               f        = fopen(pathname.name, "ab");
    if(!f)
    {
        const char* errorMessage = strerror(errno);
        motor_forceuse(errorMessage);
        motor_error_format(Log::fs(), "file {0} could not be opened: ({1}) {2}", m_filename, errno,
                           errorMessage);
        error.set(true);
    }
    else
    {
        if(offset > 0)
        {
            fseek(f, (long)offset, SEEK_SET);
        }
        else if(offset < 0)
        {
            fseek(f, (long)offset + 1, SEEK_END);
        }
        u8* data = buffer.data();
        for(processed.set(0); !done();)
        {
            size_t written
                = (processed + g_bufferSize > total)
                      ? fwrite(data, 1, motor_checked_numcast< u32 >(total - processed), f)
                      : fwrite(data, 1, g_bufferSize, f);
            processed += (u32)written;
            data += written;
            if(written == 0)
            {
                const char* errorMessage = strerror(errno);
                motor_forceuse(errorMessage);
                motor_error_format(
                    Log::fs(),
                    "could not write part of the buffer to file {0}; failed after processing "
                    "{1} bytes out of {2} ({3})",
                    m_filename, processed, total, errorMessage);
                error.set(true);
            }
        }
    }
    fflush(f);
    fclose(f);
}

}  // namespace Motor
