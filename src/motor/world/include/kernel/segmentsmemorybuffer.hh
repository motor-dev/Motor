/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_KERNEL_SEGMENTSMEMORYBUFFER_HH_
#define MOTOR_WORLD_KERNEL_SEGMENTSMEMORYBUFFER_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/scheduler/kernel/imemorybuffer.hh>

namespace Motor { namespace World {

class motor_api(WORLD) SegmentsMemoryBuffer
    : public KernelScheduler::IMemoryBuffer
    , public minitl::intrusive_list< SegmentsMemoryBuffer >::item
{
public:
    SegmentsMemoryBuffer(weak< const KernelScheduler::IMemoryHost > host);
    ~SegmentsMemoryBuffer();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
