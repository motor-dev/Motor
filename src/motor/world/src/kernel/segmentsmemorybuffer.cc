/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <kernel/segmentsmemorybuffer.hh>

namespace Motor { namespace World {

SegmentsMemoryBuffer::SegmentsMemoryBuffer(const weak< const KernelScheduler::IMemoryHost >& host)
    : IMemoryBuffer(host)
{
}

SegmentsMemoryBuffer::~SegmentsMemoryBuffer() = default;

}}  // namespace Motor::World
