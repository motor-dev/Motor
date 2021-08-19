/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

#include <cerrno>
#include <cstdio>
#include <sys/types.h>

#include <sys/sysctl.h>

namespace Motor {

size_t Environment::getProcessorCount() const
{
    int    cpuCount = 0;
    size_t len      = sizeof(cpuCount);

    int mib[4];
    mib[0] = CTL_HW;
    mib[1] = HW_NCPU;
    if(sysctl(mib, 2, &cpuCount, &len, NULL, 0) == -1)
    {
        motor_error("Could not retrieve number of processors: %s" | sys_errlist[errno]);
        cpuCount = 1;
    }
    motor_assert_recover(cpuCount >= 1, "Invalid number of CPUs returned by sysctl: %d" | cpuCount,
                         cpuCount = 1);
    motor_info("found %d CPU" | cpuCount);
    return cpuCount;
}

}  // namespace Motor
