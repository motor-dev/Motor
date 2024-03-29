/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/general.hh>

#ifdef MOTOR_COMPILER_MSVC
#    include <crtdbg.h>
#endif

namespace Motor {

GeneralAllocator::GeneralAllocator()  // NOLINT(modernize-use-equals-default)
{
#if MOTOR_ENABLE_MEMORY_TRACKING
#    ifdef MOTOR_COMPILER_MSVC
    _CrtSetDbgFlag(_CRTDBG_ALLOC_MEM_DF | _CRTDBG_LEAK_CHECK_DF);
    _crtBreakAlloc = 0;
#    endif
#endif
}

GeneralAllocator::~GeneralAllocator() noexcept = default;

void* GeneralAllocator::internal_alloc(u64 size, u64 alignment)
{
#ifdef MOTOR_COMPILER_MSVC
    return size > 0 ? ::_aligned_malloc(motor_checked_numcast< size_t >(size),
                                        motor_checked_numcast< size_t >(alignment))
                    : nullptr;
#else
    motor_forceuse(alignment);
    return size > 0 ? ::malloc(size) : nullptr;
#endif
}

bool GeneralAllocator::internal_resize(void* /*ptr*/, u64 /*size*/)
{
    return false;
}

void* GeneralAllocator::internal_realloc(void* ptr, u64 size, u64 alignment)
{
#ifdef MOTOR_COMPILER_MSVC
    return ::_aligned_realloc(ptr, motor_checked_numcast< size_t >(size),
                              motor_checked_numcast< size_t >(alignment));
#else
    motor_forceuse(alignment);
    return ::realloc(ptr, size);
#endif
}

void GeneralAllocator::internal_free(const void* pointer)
{
#ifdef MOTOR_COMPILER_MSVC
    ::_aligned_free(const_cast< void* >(pointer));
#else
    ::free(const_cast< void* >(pointer));
#endif
}

}  // namespace Motor
