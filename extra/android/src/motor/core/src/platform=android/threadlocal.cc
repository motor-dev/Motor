/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/threadlocal.hh>

#include <motor/core/timer.hh>

#include <cerrno>
#include <pthread.h>

namespace Motor {

void* ThreadLocal::tlsAlloc()
{
    pthread_key_t key;
    pthread_key_create(&key, 0);
    return reinterpret_cast< void* >(key);
}

void ThreadLocal::tlsFree(void* key)
{
    pthread_key_t k = static_cast< pthread_key_t >((uintptr_t)key);
    pthread_key_delete(k);
}

void* ThreadLocal::tlsGet(void* key)
{
    pthread_key_t k = static_cast< pthread_key_t >((uintptr_t)key);
    return const_cast< void* >(pthread_getspecific(k));
}

void ThreadLocal::tlsSet(void* key, void* value)
{
    pthread_key_t k = static_cast< pthread_key_t >((uintptr_t)key);
    pthread_setspecific(k, value);
}

}  // namespace Motor
