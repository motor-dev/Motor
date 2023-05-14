/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/core/md5.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/minitl/reverse.hh>
#include <motor/plugin.scripting.package/nodes/package.hh>
#include <packagebuilder.hh>
#include <packageloader.hh>

namespace Motor { namespace Arena {

minitl::allocator& package()
{
    return resource();
}

}}  // namespace Motor::Arena

namespace Motor { namespace PackageManager {

class PackageInstance : public minitl::refcountable
{
public:
    minitl::vector< Meta::Value > values;

    PackageInstance() : values(Arena::package())
    {
    }
};

PackageLoader::PackageLoader(const Plugin::Context& context)
    : ScriptEngine< Package >(Arena::package(), context.resourceManager)
    , m_packageBuilder(
          scoped< PackageBuilder::PackageBuilder >::create(Arena::package(), context.dataFolder))
{
}

PackageLoader::~PackageLoader() = default;

void PackageLoader::unload(const weak< const Resource::IDescription >& /*description*/,
                           Resource::Resource& handle)
{
    {
        weak< PackageInstance > instance = handle.getRefHandle< PackageInstance >();
        if(instance)
        {
            for(auto& value: minitl::reverse_view(instance->values))
            {
                if(value.isA(motor_type< const Resource::IDescription >()))
                {
                    m_manager->unload(value.type().metaclass,
                                      value.as< weak< const Resource::IDescription > >());
                }
            }
            instance->values.clear();
        }
    }
    handle.clearRefHandle();
}

void PackageLoader::runBuffer(const weak< const Package >& script, Resource::Resource& resource,
                              const minitl::allocator::block< u8 >& buffer)
{
    MD5 md5 = digest(buffer);
    motor_info_format(Log::package(), "md5 sum of package: {0}", md5);
    ref< PackageBuilder::Nodes::Package > package
        = m_packageBuilder->createPackage(script->getScriptName(), buffer);
    for(const auto& message: package->context().messages)
    {
        Log::package()->log(message.severity, MOTOR_FILE, MOTOR_LINE, message.message.c_str());
    }
    if(package->success())
    {
        ref< PackageInstance > instance = ref< PackageInstance >::create(Arena::package());
        resource.setRefHandle(instance);
        package->createObjects(m_manager, instance->values);
    }
}

void PackageLoader::reloadBuffer(const weak< const Package >& script, Resource::Resource& resource,
                                 const minitl::allocator::block< u8 >& buffer)
{
    MD5 md5 = digest(buffer);
    motor_info_format(Log::package(), "md5 sum of package: {0}", md5);
    ref< PackageBuilder::Nodes::Package > newPackage
        = m_packageBuilder->createPackage(script->getScriptName(), buffer);
    weak< PackageBuilder::Nodes::Package > oldPackage
        = resource.getRefHandle< PackageBuilder::Nodes::Package >();
    newPackage->diffFromPackage(oldPackage, m_manager);
    oldPackage.clear();
    resource.clearRefHandle();
    resource.setRefHandle(newPackage);
}

}}  // namespace Motor::PackageManager
