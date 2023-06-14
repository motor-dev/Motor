/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

#include <errno.h>
#include <stdio.h>
#include <sys/types.h>

#include <sys/sysctl.h>

namespace Motor {

size_t Environment::getProcessorCount()
{
    int    cpuCount = 0;
    size_t len      = sizeof(cpuCount);

    int mib[4];
    mib[0] = CTL_HW;
    mib[1] = HW_NCPU;
    if(sysctl(mib, 2, &cpuCount, &len, nullptr, 0) == -1)
    {
        motor_error_format(Log::system(), "Could not retrieve number of processors: {0}",
                           sys_errlist[errno]);
        cpuCount = 1;
    }
    if(motor_assert_format(cpuCount >= 1, "Invalid number of CPUs returned by sysctl: {0}",
                           cpuCount))
        cpuCount = 1;
    motor_info_format(Log::system(), "found {0} CPU", cpuCount);
    return cpuCount;
}

}  // namespace Motor
