/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/core/md5.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.scripting.package/nodes/package.hh>
#include <packagebuilder.hh>
#include <packageloader.hh>

namespace Motor { namespace Arena {

minitl::Allocator& package()
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

PackageLoader::~PackageLoader()
{
}

void PackageLoader::unload(weak< const Resource::IDescription > /*description*/,
                           Resource::Resource& handle)
{
    {
        weak< PackageInstance > instance = handle.getRefHandle< PackageInstance >();
        if(instance)
        {
            for(minitl::vector< Meta::Value >::reverse_iterator it = instance->values.rbegin();
                it != instance->values.rend(); ++it)
            {
                if(it->isA(motor_type< const Resource::IDescription >()))
                {
                    m_manager->unload(it->type().metaclass,
                                      it->as< weak< const Resource::IDescription > >());
                }
            }
            instance->values.clear();
        }
    }
    handle.clearRefHandle();
}

void PackageLoader::runBuffer(weak< const Package > script, Resource::Resource& resource,
                              const minitl::Allocator::Block< u8 >& buffer)
{
    MD5 md5 = digest(buffer);
    motor_info("md5 sum of package: %s" | md5);
    ref< PackageBuilder::Nodes::Package > package
        = m_packageBuilder->createPackage(script->getScriptName(), buffer);
    for(Meta::AST::MessageList::const_iterator it = package->context().messages.begin();
        it != package->context().messages.end(); ++it)
    {
        Logger::root()->log(it->severity, __FILE__, __LINE__, it->message.c_str());
    }
    if(package->success())
    {
        ref< PackageInstance > instance = ref< PackageInstance >::create(Arena::package());
        resource.setRefHandle(instance);
        package->createObjects(m_manager, instance->values);
    }
}

void PackageLoader::reloadBuffer(weak< const Package > script, Resource::Resource& resource,
                                 const minitl::Allocator::Block< u8 >& buffer)
{
    MD5 md5 = digest(buffer);
    motor_info("md5 sum of package: %s" | md5);
    ref< PackageBuilder::Nodes::Package > newPackage
        = m_packageBuilder->createPackage(script->getScriptName(), buffer);
    weak< PackageBuilder::Nodes::Package > oldPackage
        = resource.getRefHandle< PackageBuilder::Nodes::Package >();
    newPackage->diffFromPackage(oldPackage, m_manager);
    oldPackage = weak< PackageBuilder::Nodes::Package >();
    resource.clearRefHandle();
    resource.setRefHandle(newPackage);
}

}}  // namespace Motor::PackageManager
