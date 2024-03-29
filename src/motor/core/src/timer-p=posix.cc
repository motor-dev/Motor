/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/timer.hh>

#include <time.h>

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
#    elif defined(_PPC)
    u64               result = 0;
    unsigned long int upper, lower, tmp;
    __asm__ volatile("0:                  \n"
                     "\tmftbu   %0           \n"
                     "\tmftb    %1           \n"
                     "\tmftbu   %2           \n"
                     "\tcmpw    %2,%0        \n"
                     "\tbne     0b         \n"
                     : "=r"(upper), "=r"(lower), "=r"(tmp));
    result = upper;
    result = result << 32;
    result = result | lower;

    return (result);
#    else
    timespec t;
    clock_gettime(CLOCK_REALTIME, &t);
    return ((u64)t.tv_sec * 1000000000 + (u64)t.tv_nsec);
#    endif
#else
    timespec t {};
    clock_gettime(CLOCK_REALTIME, &t);
    return ((u64)t.tv_sec * 1000000000 + (u64)t.tv_nsec);
#endif
}

float Timer::now()
{
    timespec t {};
    clock_gettime(CLOCK_REALTIME, &t);
    static time_t s_start = t.tv_sec;
    return (float)(t.tv_sec - s_start) * 1000.0f + (float)t.tv_nsec / 1000000.0f;
}

}  // namespace Motor
