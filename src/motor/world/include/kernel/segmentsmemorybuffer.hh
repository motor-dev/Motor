/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/world/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/scheduler/kernel/imemorybuffer.hh>

namespace Motor { namespace World {

class motor_api(WORLD) SegmentsMemoryBuffer
    : public KernelScheduler::IMemoryBuffer
    , public minitl::intrusive_list< SegmentsMemoryBuffer >::item
{
public:
    explicit SegmentsMemoryBuffer(const weak< const KernelScheduler::IMemoryHost >& host);
    ~SegmentsMemoryBuffer() override;
};

}}  // namespace Motor::World
