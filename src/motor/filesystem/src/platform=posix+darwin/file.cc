/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <cerrno>
#include <cstdio>
#include <posix/file.hh>

namespace Motor {

PosixFile::PosixFile(const ifilename& filename, u64 size, time_t modifiedTime)
    : File(filename, size, modifiedTime)
{
}

PosixFile::~PosixFile() = default;

void PosixFile::doFillBuffer(const weak< File::Ticket >& ticket) const
{
    static const int g_bufferSize = 1024;

    motor_assert(ticket->file == this, "trying to read wrong file");
    ifilename::Filename pathname = m_filename.str();
    FILE*               f        = fopen(pathname.name, "rb");
    if(!f)
    {
        const char* errorMessage = strerror(errno);
        motor_forceuse(errorMessage);
        motor_error_format(Log::fs(), "file {0} could not be opened: ({1}) {2}", m_filename, errno,
                           errorMessage);
        ticket->error.set(true);
    }
    else
    {
        if(ticket->offset > 0)
        {
            fseek(f, (long)ticket->offset, SEEK_SET);
        }
        else if(ticket->offset < 0)
        {
            fseek(f, (long)ticket->offset + 1, SEEK_END);
        }
        u8* data = ticket->buffer.data();
        for(ticket->processed.set(0); !ticket->done();)
        {
            size_t read
                = (ticket->processed + g_bufferSize > ticket->total)
                      ? fread(data, 1,
                              motor_checked_numcast< u32 >(ticket->total - ticket->processed), f)
                      : fread(data, 1, g_bufferSize, f);
            ticket->processed += (u32)read;
            data += read;
            if(read == 0)
            {
                motor_error_format(
                    Log::fs(),
                    "reached premature end of file in {0} after reading {1} bytes (offset {2})",
                    m_filename, ticket->processed, ticket->total);
                ticket->error.set(true);
            }
        }
        fclose(f);
    }
}

void PosixFile::doWriteBuffer(const weak< Ticket >& ticket) const
{
    static const int g_bufferSize = 1024;

    motor_assert(ticket->file == this, "trying to write to wrong file");
    ifilename::Filename pathname = m_filename.str();
    FILE*               f        = fopen(pathname.name, "ab");
    if(!f)
    {
        const char* errorMessage = strerror(errno);
        motor_forceuse(errorMessage);
        motor_error_format(Log::fs(), "file {0} could not be opened: ({1}) {2}", m_filename, errno,
                           errorMessage);
        ticket->error.set(true);
    }
    else
    {
        if(ticket->offset > 0)
        {
            fseek(f, (long)ticket->offset, SEEK_SET);
        }
        else if(ticket->offset < 0)
        {
            fseek(f, (long)ticket->offset + 1, SEEK_END);
        }
        u8* data = ticket->buffer.data();
        for(ticket->processed.set(0); !ticket->done();)
        {
            size_t written
                = (ticket->processed + g_bufferSize > ticket->total)
                      ? fwrite(data, 1,
                               motor_checked_numcast< u32 >(ticket->total - ticket->processed), f)
                      : fwrite(data, 1, g_bufferSize, f);
            ticket->processed += (u32)written;
            data += written;
            if(written == 0)
            {
                const char* errorMessage = strerror(errno);
                motor_forceuse(errorMessage);
                motor_error_format(
                    Log::fs(),
                    "could not write part of the buffer to file {0}; failed after processing "
                    "{1} bytes out of {2} ({3})",
                    m_filename, ticket->processed, ticket->total, errorMessage);
                ticket->error.set(true);
            }
        }
    }
    fflush(f);
    fclose(f);
}

void PosixFile::refresh(u64 size, time_t modifiedTime)
{
    File::refresh(size, modifiedTime);
}

}  // namespace Motor
