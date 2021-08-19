/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/system.hh>

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
    motor_assert(size % platformPageSize() == 0,
                 "size %d is not aligned on a page boundary (page size = %d)" | size
                     | platformPageSize());
    byte* result = (byte*)VirtualAlloc(0, size, MEM_RESERVE, PAGE_NOACCESS);
    motor_assert(result, "failed to reserve memory");
    return result;
}

void SystemAllocator::platformCommit(byte* ptr, u32 start, u32 stop)
{
    motor_assert((uintptr_t)ptr % platformPageSize() == 0,
                 "pointer %p is not aligned on a page boundary (page size = %d)" | ptr
                     | platformPageSize());
    motor_assert(start % platformPageSize() == 0,
                 "offset %d is not aligned on a page boundary (page size = %d)" | start
                     | platformPageSize());
    motor_assert(stop % platformPageSize() == 0,
                 "offset %d is not aligned on a page boundary (page size = %d)" | stop
                     | platformPageSize());
    VirtualAlloc(ptr + start, stop - start, MEM_COMMIT, PAGE_READWRITE);
}

void SystemAllocator::platformRelease(byte* ptr, u32 start, u32 stop)
{
    motor_assert((uintptr_t)ptr % platformPageSize() == 0,
                 "pointer %p is not aligned on a page boundary (page size = %d)" | ptr
                     | platformPageSize());
    motor_assert(start % platformPageSize() == 0,
                 "offset %d is not aligned on a page boundary (page size = %d)" | start
                     | platformPageSize());
    motor_assert(stop % platformPageSize() == 0,
                 "offset %d is not aligned on a page boundary (page size = %d)" | stop
                     | platformPageSize());
    VirtualFree(ptr + start, stop - start, MEM_DECOMMIT);
}

void SystemAllocator::platformFree(byte* ptr, u32 size)
{
    motor_assert((uintptr_t)ptr % platformPageSize() == 0,
                 "pointer %p is not aligned on a page boundary (page size = %d)" | ptr
                     | platformPageSize());
    motor_assert(size % platformPageSize() == 0,
                 "size %p is not aligned on a page boundary (page size = %d)" | size
                     | platformPageSize());
    VirtualFree(ptr, size, MEM_RELEASE);
}

}  // namespace Motor
