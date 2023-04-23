/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/minitl/allocator.hh>

namespace Motor {

class motor_api(CORE) GeneralAllocator : public minitl::Allocator
{
public:
    GeneralAllocator();
    ~GeneralAllocator() override;

protected:
    void* internalAlloc(u64 size, u64 alignment) override;
    bool  internalResize(void* ptr, u64 size) override;
    void* internalRealloc(void* ptr, u64 size, u64 alignment) override;
    void  internalFree(const void* pointer) override;
};

}  // namespace Motor
