/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/ikernelloader.hh>

#include <motor/scheduler/kernel/icodeloader.hh>

namespace Motor { namespace KernelScheduler {

IKernelLoader::IKernelLoader(scoped< ICodeLoader >&& codeLoader)
    : m_codeLoader(minitl::move(codeLoader))
{
}

IKernelLoader::~IKernelLoader() = default;

}}  // namespace Motor::KernelScheduler
