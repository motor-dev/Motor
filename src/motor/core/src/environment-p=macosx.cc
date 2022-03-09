/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

#include <errno.h>
#include <stdio.h>
#include <sys/sysctl.h>
#include <sys/types.h>

namespace Motor {

Environment::Environment()
    : m_homeDirectory(getenv("HOME"))
    , m_dataDirectory(ipath("data"))
    , m_game("")
    , m_user(getenv("USER"))
    , m_programPath()
{
    m_homeDirectory.push_back(".motor");
}

size_t Environment::getProcessorCount() const
{
    int    cpuCount = 0;
    size_t len      = sizeof(cpuCount);

    int mib[4];
    mib[0] = CTL_HW;
    mib[1] = HW_NCPU;
    if(sysctlbyname("hw.physicalcpu", &cpuCount, &len, NULL, 0) == -1)
    {
        if(sysctl(mib, 2, &cpuCount, &len, NULL, 0) == -1)
        {
            motor_error("Could not retrieve number of processors: %s" | sys_errlist[errno]);
            cpuCount = 1;
        }
    }
    motor_assert_recover(cpuCount >= 1, "Invalid number of CPUs returned by sysctl: %d" | cpuCount,
                         cpuCount = 1);
    motor_info("found %d CPU" | cpuCount);
    return cpuCount;
}

}  // namespace Motor
