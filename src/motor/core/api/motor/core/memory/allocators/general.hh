/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_MEMORY_ALLOCATORS_GENERAL_HH_
#define MOTOR_CORE_MEMORY_ALLOCATORS_GENERAL_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/minitl/allocator.hh>

namespace Motor {

class motor_api(CORE) GeneralAllocator : public minitl::Allocator
{
public:
    GeneralAllocator();
    ~GeneralAllocator();

protected:
    virtual void* internalAlloc(u64 size, u64 alignment) override;
    virtual bool  internalResize(void* ptr, u64 size) override;
    virtual void* internalRealloc(void* ptr, u64 size, u64 alignment) override;
    virtual void  internalFree(const void* pointer) override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
