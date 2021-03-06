/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_MEMORY_ALLOCATORS_POOL_HH_
#define MOTOR_CORE_MEMORY_ALLOCATORS_POOL_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/minitl/allocator.hh>

namespace Motor {

class motor_api(CORE) PoolAllocator : public minitl::Allocator
{
public:
    PoolAllocator();
    ~PoolAllocator();

protected:
    virtual void* internalAlloc(u64 size, u64 alignment) override;
    virtual bool  internalResize(void* ptr, u64 size) override;
    virtual void* internalRealloc(void* ptr, u64 size, u64 alignment) override;
    virtual void  internalFree(const void* pointer) override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
