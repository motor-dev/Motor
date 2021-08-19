/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/timer.hh>

namespace Motor {

u64 Timer::tick()
{
#if defined(MOTOR_COMPILER_GCC)
#    if defined(_X86)
    u64 x = 0;
    __asm__ volatile(".byte 0x0f, 0x31" : "=A"(x));
    return x;
#    elif defined(_AMD64)
    unsigned hi, lo;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((u64)lo) | (((u64)hi) << 32);
#    else
    LARGE_INTEGER t;
    QueryPerformanceCounter(&t);
    return t.QuadPart;
#    endif
#else
    LARGE_INTEGER t;
    QueryPerformanceCounter(&t);
    return t.QuadPart;
#endif
}

float Timer::now()
{
    LARGE_INTEGER t, freq;
    QueryPerformanceCounter(&t);
    QueryPerformanceFrequency(&freq);
    return (float)t.QuadPart * 1000.0f / freq.QuadPart;
}

}  // namespace Motor
