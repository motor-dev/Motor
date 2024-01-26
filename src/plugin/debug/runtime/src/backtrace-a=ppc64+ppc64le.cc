/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/plugin.debug.runtime/callstack.hh>

namespace Motor { namespace Runtime {

static inline void** st_next(void** stack_pointer)
{
    void** nextStackPointer = reinterpret_cast< void** >(*stack_pointer);
    if(nextStackPointer <= stack_pointer)
    {
        return nullptr;
    }
    if(reinterpret_cast< char* >(stack_pointer) - reinterpret_cast< char* >(nextStackPointer)
       > 2 * 1024 * 1024)
    {
        return nullptr;
    }
    return nextStackPointer;
}

MOTOR_NEVER_INLINE size_t Callstack::backtrace(Address* buffer, size_t count, size_t skip)
{
    void** stackPointer;
//    stackPointer = (void**)(&buffer)-2;
#if defined(MOTOR_COMPILER_GCC) || defined(MOTOR_COMPILER_CLANG)
#    ifdef __APPLE_CC__
    stackPointer = (void**)(&buffer) - 2;
    __asm__ volatile("mr %0,r1" : "=r"(stackPointer));
#    else
    __asm__ volatile("mr %0,1" : "=r"(stackPointer));
#    endif
#else
    _asm mr stackPointer, r1;
#endif
    size_t result = 0;
    while(stackPointer && result < count)
    {
        if(skip > 0)
        {
            skip--;
        }
        else
        {
#ifdef _POWERPC64
            buffer[result].m_address = reinterpret_cast< u64 >(*(stackPointer + 1));
#else
            buffer[result].m_address = reinterpret_cast< u32 >(*(stackPointer + 1));
#endif
            result++;
        }
        stackPointer = st_next(stackPointer);
    }
    return result;
}

}}  // namespace Motor::Runtime
