/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/system.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor {
u32 SystemAllocator::platformPageSize()
{
    static SYSTEM_INFO s_systemInfo;
    static bool        s_systemInfo_acquired = (GetSystemInfo(&s_systemInfo), true);
    motor_forceuse(s_systemInfo_acquired);
    return s_systemInfo.dwPageSize;
}

byte* SystemAllocator::platformReserve(u32 size)
{
    motor_assert_format(size % platformPageSize() == 0,
                        "size {0} is not aligned on a page boundary (page size = {1})", size,
                        platformPageSize());
    byte* result = static_cast< byte* >(VirtualAlloc(nullptr, size, MEM_RESERVE, PAGE_NOACCESS));
    motor_assert(result, "failed to reserve memory");
    return result;
}

void SystemAllocator::platformCommit(byte* ptr, u32 start,
                                     u32   stop) // NOLINT(readability-non-const-parameter)
{
    motor_assert_format(reinterpret_cast< uintptr_t >(ptr)% platformPageSize() == 0,
                        "pointer {0} is not aligned on a page boundary (page size = {1})", ptr,
                        platformPageSize());
    motor_assert_format(start % platformPageSize() == 0,
                        "offset {0} is not aligned on a page boundary (page size = {1})", start,
                        platformPageSize());
    motor_assert_format(stop % platformPageSize() == 0,
                        "offset {0} is not aligned on a page boundary (page size = {1})", stop,
                        platformPageSize());
    VirtualAlloc(ptr + start, stop - start, MEM_COMMIT, PAGE_READWRITE);
}

void SystemAllocator::platformFree(byte* ptr, u32 size) // NOLINT(readability-non-const-parameter)
{
    motor_assert_format(reinterpret_cast< uintptr_t >(ptr)% platformPageSize() == 0,
                        "pointer {0} is not aligned on a page boundary (page size = {1})", ptr,
                        platformPageSize());
    motor_assert_format(size % platformPageSize() == 0,
                        "size {0} is not aligned on a page boundary (page size = {1})", size,
                        platformPageSize());
    VirtualFree(ptr, size, MEM_RELEASE);
}
} // namespace Motor
