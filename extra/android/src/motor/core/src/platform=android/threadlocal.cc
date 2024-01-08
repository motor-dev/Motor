/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/threadlocal.hh>

#include <motor/core/timer.hh>

#include <errno.h>
#include <pthread.h>

namespace Motor {

void* ThreadLocal::tlsAlloc()
{
    pthread_key_t key;
    pthread_key_create(&key, nullptr);
    return reinterpret_cast< void* >(key);
}

void ThreadLocal::tlsFree(void* key)
{
    auto k = static_cast< pthread_key_t >((uintptr_t)key);
    pthread_key_delete(k);
}

void* ThreadLocal::tlsGet(void* key)
{
    auto k = static_cast< pthread_key_t >((uintptr_t)key);
    return const_cast< void* >(pthread_getspecific(k));
}

void ThreadLocal::tlsSet(void* key, void* data)
{
    auto k = static_cast< pthread_key_t >((uintptr_t)key);
    pthread_setspecific(k, data);
}

}  // namespace Motor
