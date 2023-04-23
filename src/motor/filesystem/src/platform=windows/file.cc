/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <windows/file.hh>

#include <cstdio>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor {

Win32File::Win32File(const ifilename& filename, u64 size, u64 timestamp)
    : File(filename, size, timestamp)
{
}

Win32File::~Win32File() = default;

static void setFilePointer(const char* debugName, HANDLE file, i64 wantedOffset)
{
    LARGE_INTEGER setOffset;
    LARGE_INTEGER offset;
    if(wantedOffset >= 0)
    {
        offset.QuadPart = wantedOffset;
        SetFilePointerEx(file, offset, &setOffset, FILE_BEGIN);
        motor_assert_format(setOffset.QuadPart == wantedOffset,
                            "seek in file {0} failed: position {1} instead of {2}", debugName,
                            setOffset.QuadPart, wantedOffset);
    }
    else
    {
        offset.QuadPart = wantedOffset + 1;
        SetFilePointerEx(file, offset, &setOffset, FILE_END);
    }
}

void Win32File::doFillBuffer(const weak< File::Ticket >& ticket) const
{
    motor_assert(ticket->file == this, "trying to read wrong file");
    ifilename::Filename pathname = m_filename.str('\\');
    HANDLE h = CreateFileA(pathname.name, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0,
                           nullptr);
    if(h == INVALID_HANDLE_VALUE)
    {
        DWORD errorCode = ::GetLastError();
        motor_info_format(Log::fs(),
                          "file {0} ({1}) could not be opened: CreateFile returned an error ({2})",
                          m_filename, pathname.name, errorCode);
        ticket->error.set(true);
    }
    else
    {
        static const int s_bufferSize = 1024;
        static u8        buffer[s_bufferSize];
        u8*              target    = ticket->buffer.data();
        u32              processed = 0;
        setFilePointer(pathname.name, h, ticket->offset);
        for(ticket->processed.set(0); !ticket->done();)
        {
            DWORD read;
            if(ticket->text)
            {
                if(ticket->processed + s_bufferSize > ticket->total)
                {
                    ReadFile(h, buffer,
                             motor_checked_numcast< u32 >(ticket->total - ticket->processed), &read,
                             nullptr);
                }
                else
                {
                    ReadFile(h, buffer, s_bufferSize, &read, nullptr);
                }
                for(u32 i = 0; i < read; ++i)
                {
                    if(buffer[i] != '\r')
                    {
                        target[processed++] = buffer[i];
                    }
                }
            }
            else
            {
                if(ticket->processed + s_bufferSize > ticket->total)
                {
                    ReadFile(h, target + ticket->processed,
                             motor_checked_numcast< u32 >(ticket->total - ticket->processed), &read,
                             nullptr);
                }
                else
                {
                    ReadFile(h, target + ticket->processed, s_bufferSize, &read, nullptr);
                }
            }
            ticket->processed += read;
            if(read == 0)
            {
                motor_error_format(
                    Log::fs(),
                    "reached premature end of file in {0} after reading {1} bytes (offset {2})",
                    m_filename, ticket->processed, ticket->total);
                ticket->error.set(true);
            }
        }
        if(ticket->text && !ticket->error)
        {
            motor_assert_format(processed + 1 <= ticket->buffer.count(),
                                "buffer size is {0}; bytes processed is {1}",
                                ticket->buffer.count(), (processed + 1));
            // shrink buffer
            ticket->buffer.realloc(processed + 1);
            target[processed] = 0;
        }
    }
    CloseHandle(h);
}

void Win32File::doWriteBuffer(const weak< Ticket >& ticket) const
{
    motor_assert(ticket->file == this, "trying to read wrong file");
    ifilename::Filename pathname = m_filename.str('\\');
    HANDLE h = CreateFileA(pathname.name, GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, 0, nullptr);
    if(h == INVALID_HANDLE_VALUE)
    {
        DWORD errorCode = ::GetLastError();
        motor_info_format(Log::fs(),
                          "file {0} ({1}) could not be opened: CreateFile returned an error ({2})",
                          m_filename, pathname.name, errorCode);
        ticket->error.set(true);
    }
    else
    {
        static const int s_bufferSize = 1024;
        setFilePointer(pathname.name, h, ticket->offset);
        for(ticket->processed.set(0); !ticket->done();)
        {
            DWORD written;
            if(ticket->processed + s_bufferSize > ticket->total)
                WriteFile(h, ticket->buffer.data() + ticket->processed,
                          motor_checked_numcast< u32 >(ticket->total - ticket->processed), &written,
                          nullptr);
            else
                WriteFile(h, ticket->buffer.data() + ticket->processed, s_bufferSize, &written,
                          nullptr);
            ticket->processed += written;
            if(written == 0)
            {
                motor_error_format(
                    Log::fs(),
                    "could not write part of the buffer to file {0}; failed after processing "
                    "{1} bytes out of {2}",
                    m_filename, ticket->processed, ticket->total);
                ticket->error.set(true);
            }
        }
        CloseHandle(h);
    }
}

}  // namespace Motor
