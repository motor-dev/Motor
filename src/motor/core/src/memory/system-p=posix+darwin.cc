/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/system.hh>

#include <cerrno>
#include <sys/mman.h>
#include <unistd.h>

namespace Motor {

static u32 pageSize()
{
    static const u32 s_pageSize = sysconf(_SC_PAGE_SIZE);
    return s_pageSize;
}

u32 SystemAllocator::platformPageSize()
{
    return pageSize();
}

static inline u32 cacheAhead()
{
    static const u32 s_cacheAhead =
#if MOTOR_ENABLE_MEMORY_DEBUGGING
        0;
#else
        pageSize();
#endif
    return s_cacheAhead;
}

byte* SystemAllocator::platformReserve(u32 size)
{
    motor_assert_format(size % platformPageSize() == 0,
                        "size {0} is not aligned on a page boundary (page size = {1})", size,
                        platformPageSize());
    byte* result
        = (byte*)mmap(nullptr, size + platformPageSize(), PROT_NONE, MAP_PRIVATE | MAP_ANON, -1, 0);
    motor_assert_format(result, "failed to reserve memory for {0} bytes: {1}", size,
                        strerror(errno));
#if !MOTOR_ENABLE_MEMORY_DEBUGGING
    int failed = mprotect(result, cacheAhead(), PROT_READ | PROT_WRITE);
    motor_forceuse(failed);
    motor_assert_format(failed == 0, "failed to reserve memory for %d bytes at offset %d: %s", size,
                        0, sys_errlist[errno]);
#endif
    return result;
}

void SystemAllocator::platformCommit(byte* ptr, u32 begin, u32 end)
{
    motor_assert_format((intptr_t)ptr % platformPageSize() == 0,
                        "pointer {0} is not aligned on a page boundary (page size = {1})", ptr,
                        platformPageSize());
    motor_assert_format(begin % platformPageSize() == 0,
                        "offset {0} is not aligned on a page boundary (page size = {1})", begin,
                        platformPageSize());
    motor_assert_format(end % platformPageSize() == 0,
                        "offset {0} is not aligned on a page boundary (page size = {1})", end,
                        platformPageSize());
    int failed = mprotect((char*)ptr + begin + cacheAhead(), end - begin, PROT_READ | PROT_WRITE);
    motor_forceuse(failed);
    motor_assert_format(failed == 0, "failed to commit memory for {0} bytes at offset {1}: {2}",
                        (end - begin), begin, strerror(errno));
}

void SystemAllocator::platformFree(byte* ptr, u32 size)
{
    motor_assert_format((intptr_t)ptr % platformPageSize() == 0,
                        "pointer {0} is not aligned on a page boundary (page size = {1})", ptr,
                        platformPageSize());
    motor_assert_format(size % platformPageSize() == 0,
                        "size {0} is not aligned on a page boundary (page size = {1})", size,
                        platformPageSize());
    int failed;
#if !MOTOR_ENABLE_MEMORY_DEBUGGING
    failed = mprotect(ptr, cacheAhead(), PROT_NONE);
    motor_forceuse(failed);
    motor_assert_format(failed == 0, "failed to release memory for {0} bytes at offset {1}: {2}",
                        (end - begin), begin, strerror(errno));
#endif
    failed = munmap((char*)ptr, size);
    motor_forceuse(failed);
    motor_assert_format(failed == 0, "failed to unmap memory for {0} bytes: {1}", size,
                        strerror(errno));
}

}  // namespace Motor
