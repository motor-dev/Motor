/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor { namespace Resource {

static i_u32 s_nextLoaderId(i_u32::create(1));
ILoader::ILoader() : m_id(s_nextLoaderId++)
{
}

ILoader::~ILoader() = default;

}}  // namespace Motor::Resource
