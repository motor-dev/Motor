/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/stack.hh>

namespace Motor {

StackAllocator::StackAllocator()
{
}

StackAllocator::~StackAllocator()
{
}

void* StackAllocator::internalAlloc(u64 size, u64 alignment)
{
#ifdef _MSC_VER
    return ::_aligned_malloc(motor_checked_numcast< size_t >(size),
                             motor_checked_numcast< size_t >(alignment));
#else
    motor_forceuse(alignment);
    return ::malloc(size);
#endif
}

bool StackAllocator::internalResize(void* /*ptr*/, u64 /*size*/)
{
    return false;
}

void* StackAllocator::internalRealloc(void* ptr, u64 size, u64 alignment)
{
#ifdef _MSC_VER
    return ::_aligned_realloc(ptr, motor_checked_numcast< size_t >(size),
                              motor_checked_numcast< size_t >(alignment));
#else
    motor_forceuse(alignment);
    return ::realloc(ptr, size);
#endif
}

void StackAllocator::internalFree(const void* pointer)
{
#ifdef _MSC_VER
    ::_aligned_free(const_cast< void* >(pointer));
#else
    ::free(const_cast< void* >(pointer));
#endif
}

}  // namespace Motor
