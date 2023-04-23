/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

#include <unistd.h>

namespace Motor {

size_t Environment::getProcessorCount()
{
    return sysconf(_SC_NPROCESSORS_ONLN);
}

}  // namespace Motor
