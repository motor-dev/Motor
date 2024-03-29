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
       > 512 * 1024)
    {
        return nullptr;
    }
    return nextStackPointer;
}

MOTOR_NEVER_INLINE size_t Callstack::backtrace(Address* buffer, size_t count, size_t skip)
{
    void** stackPointer;
#ifdef MOTOR_COMPILER_MSVC
    stackPointer = 0;
#elif defined(_ARM64) && defined(_ILP32)
    __asm__ volatile("mov %w0,w29" : "=r"(stackPointer));
#elif defined(_ARM64)
    __asm__ volatile("mov %0,x29" : "=r"(stackPointer));
#else
    __asm__ volatile("mov %0,r13" : "=r"(stackPointer));
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
            buffer[result].m_address = (u64) * (stackPointer + 1);
            result++;
        }
        stackPointer = st_next(stackPointer);
    }
    return result;
}

}}  // namespace Motor::Runtime
