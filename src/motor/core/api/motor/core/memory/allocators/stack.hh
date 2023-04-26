/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/minitl/allocator.hh>

namespace Motor {

class motor_api(CORE) StackAllocator : public minitl::allocator
{
public:
    StackAllocator();
    ~StackAllocator() override;

protected:
    void* internal_alloc(u64 size, u64 alignment) override;
    bool  internal_resize(void* ptr, u64 size) override;
    void* internal_realloc(void* ptr, u64 size, u64 alignment) override;
    void  internal_free(const void* pointer) override;
};

}  // namespace Motor
