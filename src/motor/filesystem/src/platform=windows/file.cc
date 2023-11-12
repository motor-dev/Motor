/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <windows/file.hh>

#include <stdio.h>

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

ref< File::Ticket > Win32File::doBeginOperation(minitl::allocator& ticketArena,
                                                minitl::allocator& dataArena, const void* data,
                                                u32 size, i64 offset, bool text) const
{
    return ref< Ticket >::create(ticketArena, m_filename, dataArena, offset, size, text, data);
}

Win32File::Ticket::Ticket(const ifilename& filename, minitl::allocator& arena, i64 offset, u32 size,
                          bool text, const void* data)
    : File::Ticket(arena, offset, size, text, data)
    , m_filename(filename)
{
}

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

void Win32File::Ticket::fillBuffer()
{
    ifilename::Filename pathname = m_filename.str('\\');
    HANDLE h = CreateFileA(pathname.name, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0,
                           nullptr);
    if(h == INVALID_HANDLE_VALUE)
    {
        DWORD errorCode = ::GetLastError();
        motor_info_format(Log::fs(),
                          "file {0} ({1}) could not be opened: CreateFile returned an error ({2})",
                          m_filename, pathname.name, errorCode);
        error.set(true);
    }
    else
    {
        static const int s_bufferSize = 1024;
        u8*              target       = buffer.data();
        setFilePointer(pathname.name, h, offset);
        for(processed.set(0); !done();)
        {
            DWORD read;
            if(processed + s_bufferSize > total)
            {
                ReadFile(h, target + processed, motor_checked_numcast< u32 >(total - processed),
                         &read, nullptr);
            }
            else
            {
                ReadFile(h, target + processed, s_bufferSize, &read, nullptr);
            }
            processed += read;
            if(read == 0)
            {
                motor_error_format(
                    Log::fs(),
                    "reached premature end of file in {0} after reading {1} bytes (offset {2})",
                    m_filename, processed, total);
                error.set(true);
            }
        }
        if(text && !error)
        {
            motor_assert_format(processed + 1 <= buffer.count(),
                                "buffer size is {0}; bytes processed is {1}", buffer.count(),
                                (processed + 1));
            // shrink buffer
            buffer.realloc(processed + 1);
            target[processed] = 0;
        }
    }
    CloseHandle(h);
}

void Win32File::Ticket::writeBuffer()
{
    ifilename::Filename pathname = m_filename.str('\\');
    HANDLE h = CreateFileA(pathname.name, GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, 0, nullptr);
    if(h == INVALID_HANDLE_VALUE)
    {
        DWORD errorCode = ::GetLastError();
        motor_info_format(Log::fs(),
                          "file {0} ({1}) could not be opened: CreateFile returned an error ({2})",
                          m_filename, pathname.name, errorCode);
        error.set(true);
    }
    else
    {
        static const int s_bufferSize = 1024;
        setFilePointer(pathname.name, h, offset);
        for(processed.set(0); !done();)
        {
            DWORD written;
            if(processed + s_bufferSize > total)
                WriteFile(h, buffer.data() + processed,
                          motor_checked_numcast< u32 >(total - processed), &written, nullptr);
            else
                WriteFile(h, buffer.data() + processed, s_bufferSize, &written, nullptr);
            processed += written;
            if(written == 0)
            {
                motor_error_format(
                    Log::fs(),
                    "could not write part of the buffer to file {0}; failed after processing "
                    "{1} bytes out of {2}",
                    m_filename, processed, total);
                error.set(true);
            }
        }
        CloseHandle(h);
    }
}

}  // namespace Motor
