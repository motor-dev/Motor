/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/system.hh>

#include <errno.h>
#include <sys/mman.h>
#include <unistd.h>

namespace Motor {
static u32 pageSize()
{
    static const u32 s_pageSize = static_cast< u32 >(sysconf(_SC_PAGE_SIZE));
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
    const auto result
        = static_cast< byte* >(mmap(nullptr, size + platformPageSize(), PROT_NONE,
                                    MAP_PRIVATE | MAP_ANON, -1,
                                    0));
    motor_assert_format(result, "failed to reserve memory for {0} bytes: {1}", size,
                        strerror(errno));
#if !MOTOR_ENABLE_MEMORY_DEBUGGING

#endif
    return result;
}

void SystemAllocator::platformCommit(byte* ptr, u32 start, u32 stop)
{
    motor_assert_format(reinterpret_cast< intptr_t >(ptr)% platformPageSize() == 0,
                        "pointer {0} is not aligned on a page boundary (page size = {1})", ptr,
                        platformPageSize());
    motor_assert_format(start % platformPageSize() == 0,
                        "offset {0} is not aligned on a page boundary (page size = {1})", start,
                        platformPageSize());
    motor_assert_format(stop % platformPageSize() == 0,
                        "offset {0} is not aligned on a page boundary (page size = {1})", stop,
                        platformPageSize());
    const int failed = mprotect(reinterpret_cast< char* >(ptr) + start + cacheAhead(), stop - start,
                                PROT_READ | PROT_WRITE);
    motor_forceuse(failed);
    motor_assert_format(failed == 0, "failed to commit memory for {0} bytes at offset {1}: {2}",
                        (stop - start), start, strerror(errno));
}

void SystemAllocator::platformFree(byte* ptr, u32 size)
{
    motor_assert_format(reinterpret_cast< intptr_t >(ptr)% platformPageSize() == 0,
                        "pointer {0} is not aligned on a page boundary (page size = {1})", ptr,
                        platformPageSize());
    motor_assert_format(size % platformPageSize() == 0,
                        "size {0} is not aligned on a page boundary (page size = {1})", size,
                        platformPageSize());
    int failed;
#if !MOTOR_ENABLE_MEMORY_DEBUGGING

#endif
    failed = munmap((char*)ptr, size);
    motor_forceuse(failed);
    motor_assert_format(failed == 0, "failed to unmap memory for {0} bytes: {1}", size,
                        strerror(errno));
}
} // namespace Motor
